using System.IO;
using Npgsql;

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


var app = builder.Build();

app.UseHttpsRedirection();

app.MapMethods("/", new[] { "GET", "POST" }, () => {
    return Results.Content(html_template_str, "text/html");
});

app.Run();

