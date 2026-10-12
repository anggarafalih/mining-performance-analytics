namespace MiningReport.Models;

public class Project
{
    public string ProjectCode { get; set; } = string.Empty;
    public string ProjectName { get; set; } = string.Empty;
    public string Location { get; set; } = string.Empty;
    public string MaterialType { get; set; } = string.Empty;
}

public class Equipment
{
    public string EquipmentCode { get; set; } = string.Empty;
    public string EquipmentType { get; set; } = string.Empty;
    public string ProjectCode { get; set; } = string.Empty;
    public string Model { get; set; } = string.Empty;
    public decimal Capacity { get; set; }
    public string CapacityUnit { get; set; } = string.Empty;
}
