Attribute VB_Name = "Module_RefreshAndExport"
Option Explicit

' ==============================================================================
' Project: Mining Production Performance Analytics (PT PAMA Portfolio)
' Module: Module_RefreshAndExport
' Description: Otomasi refresh semua query & pivot table, hitung ulang metrik,
'              ekspor sheet Dashboard ke PDF bertanggal di folder output/,
'              dan pencatatan audit log ke sheet Log.
' ==============================================================================

Public Sub RefreshAndExport()
    Dim wsDashboard As Worksheet
    Dim wsLog As Worksheet
    Dim outputPath As String
    Dim fileName As String
    Dim fullFilePath As String
    Dim startTime As Double
    Dim executionDuration As Double
    Dim logRow As Long
    Dim currentProject As String
    Dim currentDateStr As String
    
    startTime = Timer
    currentDateStr = Format(Now, "yyyy-mm-dd")
    
    On Error GoTo ErrorHandler
    
    ' Konfigurasi optimasi aplikasi
    Application.ScreenUpdating = False
    Application.DisplayAlerts = False
    Application.EnableEvents = False
    Application.StatusBar = "Sedang merefresh koneksi data dan PivotTable..."
    
    ' Validasi worksheet
    Set wsDashboard = ThisWorkbook.Sheets("Dashboard")
    
    ' Pastikan sheet Log ada, jika belum ada maka dibuat
    On Error Resume Next
    Set wsLog = ThisWorkbook.Sheets("Log")
    On Error GoTo ErrorHandler
    
    If wsLog Is Nothing Then
        Set wsLog = ThisWorkbook.Sheets.Add(After:=ThisWorkbook.Sheets(ThisWorkbook.Sheets.Count))
        wsLog.Name = "Log"
        wsLog.Cells(1, 1).Value = "Timestamp"
        wsLog.Cells(1, 2).Value = "Status"
        wsLog.Cells(1, 3).Value = "Duration (s)"
        wsLog.Cells(1, 4).Value = "Output File"
        wsLog.Cells(1, 5).Value = "Message"
        wsLog.Range("A1:E1").Font.Bold = True
        wsLog.Columns("A:E").AutoFit
    End If
    
    ' 1. Refresh semua Query dan PivotTable
    ThisWorkbook.RefreshAll
    
    ' Menunggu kalkulasi async query selesai (jika menggunakan Power Query OLEDB)
    On Error Resume Next
    Application.CalculateUntilAsyncQueriesDone
    On Error GoTo ErrorHandler
    
    ' 2. Hitung ulang seluruh rumus di workbook
    Application.CalculateFull
    
    ' 3. Tentukan path folder output (relatif terhadap direktori workbook)
    outputPath = ThisWorkbook.Path & Application.PathSeparator & "output"
    If Dir(outputPath, vbDirectory) = "" Then
        MkDir outputPath
    End If
    
    ' 4. Generate nama file PDF
    fileName = "Laporan_Produksi_Tambang_" & currentDateStr & ".pdf"
    fullFilePath = outputPath & Application.PathSeparator & fileName
    
    ' 5. Setup orientasi cetak A4 Landscape untuk sheet Dashboard
    With wsDashboard.PageSetup
        .Orientation = xlLandscape
        .PaperSize = xlPaperA4
        .Zoom = False
        .FitToPagesWide = 1
        .FitToPagesTall = 1
        .CenterHorizontally = True
        .CenterVertically = False
    End With
    
    ' 6. Ekspor Dashboard ke format PDF
    wsDashboard.ExportAsFixedFormat _
        Type:=xlTypePDF, _
        fileName:=fullFilePath, _
        Quality:=xlQualityStandard, _
        IncludeDocProperties:=True, _
        IgnorePrintAreas:=False, _
        OpenAfterPublish:=False
    
    executionDuration = Round(Timer - startTime, 2)
    
    ' 7. Catat audit log ke sheet Log
    logRow = wsLog.Cells(wsLog.Rows.Count, 1).End(xlUp).Row + 1
    wsLog.Cells(logRow, 1).Value = Format(Now, "yyyy-mm-dd hh:mm:ss")
    wsLog.Cells(logRow, 2).Value = "SUCCESS"
    wsLog.Cells(logRow, 3).Value = executionDuration
    wsLog.Cells(logRow, 4).Value = fileName
    wsLog.Cells(logRow, 5).Value = "Refresh dan ekspor PDF selesai tanpa kendala."
    wsLog.Columns("A:E").AutoFit
    
    ' Kembalikan pengaturan aplikasi
    Application.StatusBar = False
    Application.ScreenUpdating = True
    Application.DisplayAlerts = True
    Application.EnableEvents = True
    
    MsgBox "Laporan berhasil diekspor ke:" & vbCrLf & fullFilePath & vbCrLf & _
           "Durasi: " & executionDuration & " detik.", vbInformation, "Mining Performance Analytics"
    Exit Sub

ErrorHandler:
    executionDuration = Round(Timer - startTime, 2)
    
    ' Catat log error
    If Not wsLog Is Nothing Then
        logRow = wsLog.Cells(wsLog.Rows.Count, 1).End(xlUp).Row + 1
        wsLog.Cells(logRow, 1).Value = Format(Now, "yyyy-mm-dd hh:mm:ss")
        wsLog.Cells(logRow, 2).Value = "ERROR"
        wsLog.Cells(logRow, 3).Value = executionDuration
        wsLog.Cells(logRow, 4).Value = "-"
        wsLog.Cells(logRow, 5).Value = "Error " & Err.Number & ": " & Err.Description
        wsLog.Columns("A:E").AutoFit
    End If
    
    ' Pulihkan state aplikasi
    Application.StatusBar = False
    Application.ScreenUpdating = True
    Application.DisplayAlerts = True
    Application.EnableEvents = True
    
    MsgBox "Terjadi kesalahan saat memproses laporan:" & vbCrLf & _
           Err.Description & " (Code: " & Err.Number & ")", vbCritical, "Error Refresh & Export"
End Sub
