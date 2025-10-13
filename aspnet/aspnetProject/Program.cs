using System.IO;
using Npgsql;
using Stubble.Core.Interfaces;
using Stubble.Core.Builders;
using Isopoh.Cryptography.Argon2;

using System; //time; console write for debug
using System.Diagnostics;


var builder = WebApplication.CreateBuilder(args);

string html_template_str = File.ReadAllText("/etc/config/html/html_template").Trim();
var ConnStringBuilder = new NpgsqlConnectionStringBuilder {
    Host = File.ReadAllText("/etc/config/db/host").Trim(),
    Port = int.Parse(File.ReadAllText("/etc/config/db/port").Trim()),
    Database = File.ReadAllText("/etc/config/db/name").Trim(),
    Username = File.ReadAllText("/etc/config/db/user").Trim(),
    Password = File.ReadAllText("/etc/config/db/password").Trim(),
    SslMode = SslMode.Prefer // optional parameter
};
string connectionString = ConnStringBuilder.ConnectionString;
var dataSource = new NpgsqlDataSourceBuilder(connectionString).Build();
builder.Services.AddSingleton(dataSource);
builder.Services.AddSingleton<IStubbleRenderer>(new StubbleBuilder().Build());

var app = builder.Build();
//app.UseHttpsRedirection();

app.MapMethods("/", new[] { "GET", "POST" }, async (HttpRequest request, NpgsqlDataSource db, IStubbleRenderer mustache) => {
    Stopwatch stopwatch = new Stopwatch();
    stopwatch.Start(); 

    await using var conn = await db.OpenConnectionAsync();
    await using var cmd = new NpgsqlCommand("SELECT * FROM users ORDER BY id;", conn);
    var select_users = await cmd.ExecuteReaderAsync();

    string tc = "";
    while (await select_users.ReadAsync()) {
        tc += "<tr>";
        tc += $"<td>{select_users.GetInt32(0).ToString()}</td>"; // id
        tc += $"<td>{select_users.GetString(1)}</td>"; // username
        tc += $"<td>{select_users.GetString(2)}</td>"; // password
        if (select_users.IsDBNull(3)) {
            tc += "<td>NULL</td>";
        } else {
            tc += $"<td>{select_users.GetString(3)}</td>"; // raw_password
        }
        tc += "</tr>";
    }


    string form_username = "";
    string form_password = "";
    string request_result = "";
    await using var conn2 = await db.OpenConnectionAsync();
    if (HttpMethods.IsPost(request.Method)) {
        var form = await request.ReadFormAsync();
        form_username = form["username"];
        form_password = form["password"];

        request_result = "❌ Invalid Credentials";
        await using var select_username = new NpgsqlCommand("SELECT id, username, password FROM users WHERE username=($1);", conn2) {
            Parameters = {
                new() {Value = form_username}
            }
        };
        var username_result = await select_username.ExecuteReaderAsync();
        if (await username_result.ReadAsync()) {
            if (Argon2.Verify(
                    username_result.GetString(2),
                    form_password
            )) {
                request_result = "✅ Credentials Verified";
            }
        }
    }

    var model = new
    {
        CURRENT_TIME = DateTime.Now,
        TABLE_CONTENTS = tc,
        FORM_USERNAME_VALUE = form_username,
        REQUEST_RESULT = request_result,
        STATUS = $"{stopwatch.Elapsed} from aspnet",
    };
    
    return Results.Content(
        mustache.Render(html_template_str, model),
        "text/html; charset=utf-8"
    );

});

app.Run();

