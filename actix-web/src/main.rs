use std::fs;
use std::path::Path;
use std::collections::HashMap;
use serde::Serialize;
use chrono::Local;
use std::time::Instant;
use mustache;
use sqlx::PgPool;
use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use argon2::{Argon2, PasswordHash, PasswordVerifier};

fn verify_password(user_input: &str, stored_hash: &str) -> bool { //let ChatGPT make this
    let parsed_hash = match PasswordHash::new(stored_hash) {
        Ok(h) => h,
        Err(_) => return false, // invalid hash stored
    };
    Argon2::default()
        .verify_password(user_input.as_bytes(), &parsed_hash)
        .is_ok()
}

#[derive(Serialize)]
#[serde(rename_all = "UPPERCASE")] // compiler wants snake case while template uses all caps
struct TemplateData<'a> {
    current_time : &'a str,
    table_contents: &'a str,
    form_username_value: &'a str,
    request_result: &'a str,
    status: &'a str,
}

#[derive(Serialize, sqlx::FromRow)]
struct User {
    id: i32,
    username: String,
    password: String,
    raw_password: Option<String>
}

async fn index(form: Option<web::Form<HashMap<String,String>>>, html_template: web::Data<mustache::Template>, db_pool: web::Data<PgPool>) -> impl Responder {
    let start: Instant = Instant::now();

    let rows: Vec<User>;
    match sqlx::query_as::<_, User>("SELECT * FROM users ORDER BY id;")
        .fetch_all(db_pool.get_ref()).await 
    {    
        Ok(result) => rows=result,
        Err(e) => {return HttpResponse::InternalServerError().body(e.to_string())},
    }

    let mut table_html = String::from("");
    for user in rows {
        let p = match user.raw_password {
            Some(s) => s,
            None => String::from("NULL")
        };
        table_html += &format!(
            r#"<tr>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
            </tr>"#,
            user.id,
            user.username,
            user.password,
            p
        );
    }

    let post: bool;
    let form_username: &str = form.as_ref().and_then(|f| f.get("username")).map(|s| s.as_str()).unwrap_or("");
    let form_password: &str = form.as_ref().and_then(|f| f.get("password")).map(|s| s.as_str()).unwrap_or("");
    match form {
        Some(_) => {
            post = true;
            //println!("u-{}!!!!p-{}", form_username, form_password);
        },
        None => post = false,
    }
    let mut request_result = "";
    if post {
        request_result = "❌ Invalid Credentials";

        let row: Option<User>;
        match sqlx::query_as::<_, User>("SELECT * FROM users WHERE username=$1;")
            .bind(form_username)
            .fetch_optional(db_pool.get_ref()).await 
        {
            Ok(result) => row=result,
            Err(_e) => {
                //println!("{:?}", _e); // todo return actual database error
                row = None;
            },
        }

        if let Some(user) = row {
            println!("{} {}", &form_password, &user.password);
            if verify_password(form_password, &user.password) {
                request_result = "✅ Credentials Verified";
            }
        }
    }

    let template_values = TemplateData {
        current_time : &Local::now().to_string(),
        table_contents: &table_html,
        form_username_value: form_username,
        request_result: request_result,
        status: &format!("{:.4?} from Actix-Web", start.elapsed()),
    };

    let mut renderer_out= Vec::new();
    match html_template.render(&mut renderer_out, &template_values) {
        Ok(_) => {},
        Err(e) => {return HttpResponse::InternalServerError().body(e.to_string())}
    }
    match String::from_utf8(renderer_out) {
        Ok(h) => {
            HttpResponse::Ok()
                .content_type("text/html; charset=utf-8")
                .body(h)
        },
        Err(e) => {HttpResponse::InternalServerError().body(e.to_string())}
    }
    
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let conf_dir = "/etc/config/";
    let mut config: HashMap<&str, String> = HashMap::new();
    for s in [
        "db/host",
        "db/port",
        "db/name",
        "db/user",
        "db/password",
        "html/html_template"
    ] {
        let path = Path::new(conf_dir).join(s);
        let content = fs::read_to_string(path).unwrap().trim().to_string();
        config.insert(
            s,
            content
        );
    }

    let database_url: String = format!(
        "postgres://{}:{}@{}:{}/{}",
        config.get("db/user").unwrap(),
        config.get("db/password").unwrap(),
        config.get("db/host").unwrap(),
        config.get("db/port").unwrap(),
        config.get("db/name").unwrap(),
    );

    let db_pool = PgPool::connect(&database_url).await
        .expect("Failed to create DB pool");

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(db_pool.clone()))
            .app_data(web::Data::new(
                mustache::compile_str(
                    config.get("html/html_template").unwrap()
                ).unwrap()))
            .route("/",
                web::route()
                    .guard(actix_web::guard::Any(actix_web::guard::Get())
                    .or(actix_web::guard::Post()))
                    .to(index)
            )
    })
    .bind(("0.0.0.0", 80))?
    .run()
    .await

}
