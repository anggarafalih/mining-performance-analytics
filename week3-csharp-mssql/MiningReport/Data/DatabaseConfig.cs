using Microsoft.Extensions.Configuration;

namespace MiningReport.Data;

public class DatabaseConfig
{
    public string ConnectionString { get; set; } = string.Empty;

    public static DatabaseConfig Load()
    {
        var builder = new ConfigurationBuilder()
            .SetBasePath(AppContext.BaseDirectory)
            .AddJsonFile("appsettings.json", optional: true, reloadOnChange: true)
            .AddEnvironmentVariables();

        var configuration = builder.Build();
        var connStr = configuration.GetConnectionString("MiningDatabase") 
            ?? "Server=localhost,1433;Database=mining_analytics;User Id=sa;Password=PamaSecure2026!;TrustServerCertificate=True;Connect Timeout=5;";

        return new DatabaseConfig { ConnectionString = connStr };
    }
}
