using System.IO;
using Npgsql;
using Stubble.Core.Interfaces;
using Stubble.Core.Builders;

using System; //debug

var builder = WebApplication.CreateBuilder(args);

string html_template_str = File.ReadAllText("/etc/config/html/html_template").Trim();
var ConnStringBuilder = new NpgsqlConnectionStringBuilder
{
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

app.UseHttpsRedirection();

app.MapMethods("/", new[] { "GET", "POST" }, async (HttpRequest request, NpgsqlDataSource db, IStubbleRenderer mustache) => {
    await using var conn = await db.OpenConnectionAsync();
    await using var cmd = new NpgsqlCommand("SELECT NOW()", conn);
    var serverTime = await cmd.ExecuteScalarAsync();



    string form_username = "";
    string form_password = "";
    if (HttpMethods.IsPost(request.Method)) {
        var form = await request.ReadFormAsync();
        form_username = form["username"];
        form_password = form["password"];
        Console.WriteLine($"post password:{form_password}");
    }

    var model = new {
        STATUS = "aspnet",
        FORM_USERNAME_VALUE = form_username,
    };

    return Results.Content(
        mustache.Render(html_template_str, model),
        "text/html"
    );

});

app.Run();

