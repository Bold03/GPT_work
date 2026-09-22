using System.Net.Http.Json;
using System.Text.Json;

var http = new HttpClient { BaseAddress = new Uri("http://127.0.0.1:8765") };
Console.WriteLine("X-Plane AI Copilot Console (.NET 8)");
Console.WriteLine("Type a command, 'status', or 'quit'. Examples: set heading 270 | nyalakan lampu pendaratan");

while (true)
{
    Console.Write("copilot> ");
    var line = Console.ReadLine()?.Trim();
    if (string.IsNullOrWhiteSpace(line)) continue;
    if (line.Equals("quit", StringComparison.OrdinalIgnoreCase)) break;
    try
    {
        if (line.Equals("status", StringComparison.OrdinalIgnoreCase))
        {
            var json = await http.GetStringAsync("/status");
            using var doc = JsonDocument.Parse(json);
            Console.WriteLine(JsonSerializer.Serialize(doc.RootElement, new JsonSerializerOptions { WriteIndented = true }));
        }
        else
        {
            var res = await http.PostAsJsonAsync("/command", new { text = line });
            Console.WriteLine(await res.Content.ReadAsStringAsync());
        }
    }
    catch (Exception ex) { Console.WriteLine($"ERROR: {ex.Message}"); }
}
