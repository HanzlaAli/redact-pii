# C# to Python Conversion - Side-by-Side Comparison

## Project Structure Comparison

### C# Original
```
redact-pii/
├── Program.cs
├── appsettings.json
├── Configuration/
│   ├── AzureDocumentIntelligenceSettings.cs
│   ├── AzureLanguageSettings.cs
│   └── OpenAiSettings.cs
├── Services/
│   ├── PiiRedactionService.cs
│   ├── TextExtractionService.cs
│   ├── PiiDetectionService.cs
│   ├── ImageRedactionService.cs
│   └── Providers/
│       ├── AzurePiiDetectionServiceProvider.cs
│       └── OpenAiPiiDetectionServiceProvider.cs
├── Models/
│   └── ImageRedactionResult.cs
├── Interfaces/
│   └── IPiiDetectionServiceProvider.cs
└── Extensions/
    └── WebApplicationBuilderExtensions.cs
```

### Python Conversion
```
python-version/
├── app.py
├── config.py
├── .env (gitignored)
├── .env.example
├── services/
│   ├── pii_redaction_service.py
│   ├── text_extraction_service.py
│   ├── pii_detection_service.py
│   └── image_redaction_service.py
├── providers/
│   ├── azure_pii_detection_provider.py
│   └── openai_pii_detection_provider.py
├── models/
│   └── __init__.py
├── interfaces/
│   └── __init__.py
└── [test files and docs]
```

## Code Comparison

### 1. Application Entry Point

**C# (Program.cs)**
```csharp
var builder = WebApplication.CreateBuilder(args)
    .AddAzureDocumentIntelligenceServices()
    .AddAzureLanguageServices()
    .AddApplicationServices();

var app = builder.Build();
app.UseHttpsRedirection();

app.MapPost("/redact-pii", async (IFormFile file, 
    PiiRedactionService redactPiiService, 
    CancellationToken cancellationToken) =>
{
    await using var fileStream = file.OpenReadStream();
    using var sourceImageStream = new MemoryStream();
    await fileStream.CopyToAsync(sourceImageStream, cancellationToken);
    var sourceImageBytes = sourceImageStream.ToArray();

    var (redactedImageContent, redactedImageContentType) =
        await redactPiiService.RedactPii(sourceImageBytes, cancellationToken);

    return Results.File(redactedImageContent, 
        contentType: redactedImageContentType,
        fileDownloadName: file.FileName);
})
.DisableAntiforgery();

app.Run();
```

**Python (app.py)**
```python
from flask import Flask, request, send_file
import io

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/redact-pii', methods=['POST'])
def redact_pii():
    file = request.files['file']
    file_content = file.read()
    
    redaction_service = get_redaction_service()
    redacted_image_bytes, content_type = redaction_service.redact_pii(
        file_content
    )
    
    return send_file(
        io.BytesIO(redacted_image_bytes),
        mimetype=content_type,
        as_attachment=True,
        download_name=secure_filename(file.filename)
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 2. Configuration

**C# (appsettings.json)**
```json
{
  "Azure": {
    "DocumentIntelligence": {
      "Endpoint": "https://...",
      "Key": "..."
    },
    "Language": {
      "Endpoint": "https://...",
      "Key": "..."
    }
  }
}
```

**Python (.env)**
```env
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://...
AZURE_DOCUMENT_INTELLIGENCE_KEY=...
AZURE_LANGUAGE_ENDPOINT=https://...
AZURE_LANGUAGE_KEY=...
```

**C# (Settings Class)**
```csharp
internal sealed class AzureDocumentIntelligenceSettings
{
    public const string ConfigurationPath = "Azure:DocumentIntelligence";
    
    [Required, Url]
    public required string Endpoint { get; set; }
    
    [Required]
    public required string Key { get; set; }
}
```

**Python (config.py)**
```python
class Config:
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv(
        'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT'
    )
    AZURE_DOCUMENT_INTELLIGENCE_KEY = os.getenv(
        'AZURE_DOCUMENT_INTELLIGENCE_KEY'
    )
    
    @staticmethod
    def validate():
        required_configs = [
            ('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT', 
             Config.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT),
        ]
        missing = [name for name, value in required_configs if not value]
        if missing:
            raise ValueError(f"Missing: {', '.join(missing)}")
```

### 3. Text Extraction Service

**C# (TextExtractionService.cs)**
```csharp
internal sealed class TextExtractionService
{
    private readonly DocumentAnalysisClient _documentAnalysisClient;
    
    public TextExtractionService(DocumentAnalysisClient documentAnalysisClient)
    {
        _documentAnalysisClient = documentAnalysisClient;
    }
    
    public async Task<AnalyzeResult> ExtractTextFromImage(
        byte[] sourceImageBytes,
        CancellationToken cancellationToken)
    {
        using var sourceImageStream = new MemoryStream(sourceImageBytes);
        
        var documentAnalysisOperation = 
            await _documentAnalysisClient.AnalyzeDocumentAsync(
                WaitUntil.Completed, 
                "prebuilt-read", 
                document: sourceImageStream,
                cancellationToken: cancellationToken);

        return documentAnalysisOperation.Value;
    }
}
```

**Python (text_extraction_service.py)**
```python
class TextExtractionService:
    def __init__(self, endpoint: str, key: str):
        self.credential = AzureKeyCredential(key)
        self.client = DocumentAnalysisClient(
            endpoint=endpoint, 
            credential=self.credential
        )
    
    def extract_text_from_image(
        self, 
        image_bytes: bytes
    ) -> Tuple[str, List[DocumentWord]]:
        poller = self.client.begin_analyze_document(
            "prebuilt-read", 
            image_bytes
        )
        result = poller.result()
        
        full_text = result.content
        document_words = []
        
        for page in result.pages:
            for word in page.words:
                polygon = [coord for point in word.polygon 
                          for coord in (point.x, point.y)]
                bounding_box = BoundingBox.from_polygon(polygon)
                
                document_words.append(DocumentWord(
                    content=word.content,
                    bounding_box=bounding_box,
                    confidence=word.confidence
                ))
        
        return full_text, document_words
```

### 4. PII Detection Service

**C# (PiiDetectionService.cs)**
```csharp
internal sealed class PiiDetectionService
{
    private readonly IPiiDetectionServiceProvider _provider;

    public PiiDetectionService(
        [FromKeyedServices("azure")] 
        IPiiDetectionServiceProvider provider)
    {
        _provider = provider;
    }

    public async Task<ISet<string>> ExtractPii(
        string textContent, 
        CancellationToken cancellationToken = default)
    {
        var piiDetectionResult = await _provider.DetectPii(
            textContent, 
            cancellationToken
        );
        return piiDetectionResult.ToHashSet();
    }
}
```

**Python (pii_detection_service.py)**
```python
class PiiDetectionService:
    def __init__(
        self, 
        pii_detection_provider: IPiiDetectionServiceProvider
    ):
        self.pii_detection_provider = pii_detection_provider
    
    def extract_pii(self, text_content: str) -> Set[str]:
        pii_values = self.pii_detection_provider.detect_pii(
            text_content
        )
        return set(pii_values)
```

### 5. Image Redaction Service

**C# (ImageRedactionService.cs)**
```csharp
internal sealed class ImageRedactionService
{
    public ImageRedactionResult RedactImage(
        byte[] sourceImagesBytes,
        IEnumerable<SKRect> redactionAreas)
    {
        var bitmap = SKBitmap.Decode(sourceImagesBytes);
        using var canvas = new SKCanvas(bitmap);
        
        var paint = new SKPaint
        {
            Color = SKColors.Black,
            Style = SKPaintStyle.Fill
        };

        foreach (var redactionArea in redactionAreas)
        {
            canvas.DrawRect(redactionArea, paint);
        }

        using var editedImage = SKImage.FromBitmap(bitmap);
        using var editedImageData = editedImage.Encode(
            SKEncodedImageFormat.Png, 
            100
        );

        return new ImageRedactionResult(
            editedImageData.ToArray(), 
            MediaTypeNames.Image.Png
        );
    }
}
```

**Python (image_redaction_service.py)**
```python
class ImageRedactionService:
    def redact_image(
        self, 
        source_image_bytes: bytes, 
        redaction_areas: List[BoundingBox]
    ) -> ImageRedactionResult:
        image = Image.open(io.BytesIO(source_image_bytes))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        draw = ImageDraw.Draw(image)
        
        for bbox in redaction_areas:
            rectangle = [
                bbox.x,
                bbox.y,
                bbox.x + bbox.width,
                bbox.y + bbox.height
            ]
            draw.rectangle(rectangle, fill='black')
        
        output_buffer = io.BytesIO()
        image.save(output_buffer, format='PNG')
        redacted_bytes = output_buffer.getvalue()
        
        return ImageRedactionResult(
            content=redacted_bytes,
            content_type='image/png'
        )
```

### 6. Azure PII Detection Provider

**C# (AzurePiiDetectionServiceProvider.cs)**
```csharp
internal sealed class AzurePiiDetectionServiceProvider 
    : IPiiDetectionServiceProvider
{
    private readonly TextAnalyticsClient _textAnalyticsClient;
    
    public async Task<IEnumerable<string>> DetectPii(
        string textContent,
        CancellationToken cancellationToken = default)
    {
        PiiEntityCollection response = 
            await _textAnalyticsClient.RecognizePiiEntitiesAsync(
                textContent, 
                cancellationToken: cancellationToken
            );

        return response.Select(x => x.Text);
    }
}
```

**Python (azure_pii_detection_provider.py)**
```python
class AzurePiiDetectionServiceProvider(IPiiDetectionServiceProvider):
    def __init__(self, endpoint: str, key: str):
        self.credential = AzureKeyCredential(key)
        self.client = TextAnalyticsClient(
            endpoint=endpoint, 
            credential=self.credential
        )
    
    def detect_pii(self, text_content: str) -> List[str]:
        response = self.client.recognize_pii_entities(
            [text_content], 
            language="en"
        )
        
        pii_entities = []
        for doc in response:
            if not doc.is_error:
                for entity in doc.entities:
                    pii_entities.append(entity.text)
        
        return pii_entities
```

### 7. Dependency Injection

**C# (WebApplicationBuilderExtensions.cs)**
```csharp
public static WebApplicationBuilder AddApplicationServices(
    this WebApplicationBuilder builder)
{
    builder.Services.AddKeyedScoped<IPiiDetectionServiceProvider, 
        AzurePiiDetectionServiceProvider>("azure");

    builder.Services.AddScoped<ImageRedactionService>();
    builder.Services.AddScoped<TextExtractionService>();
    builder.Services.AddScoped<PiiDetectionService>();
    builder.Services.AddScoped<PiiRedactionService>();

    return builder;
}
```

**Python (app.py - Factory Function)**
```python
def get_redaction_service():
    """Factory function to create PII redaction service."""
    azure_pii_provider = AzurePiiDetectionServiceProvider(
        endpoint=Config.AZURE_LANGUAGE_ENDPOINT,
        key=Config.AZURE_LANGUAGE_KEY
    )
    
    text_extraction_service = TextExtractionService(
        endpoint=Config.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT,
        key=Config.AZURE_DOCUMENT_INTELLIGENCE_KEY
    )
    
    pii_detection_service = PiiDetectionService(
        pii_detection_provider=azure_pii_provider
    )
    
    image_redaction_service = ImageRedactionService()
    
    return PiiRedactionService(
        pii_detection_service=pii_detection_service,
        text_extraction_service=text_extraction_service,
        image_redaction_service=image_redaction_service
    )
```

## Key Differences Summary

### Language Features

| Feature | C# | Python |
|---------|----|----|---|
| Type System | Static, strongly typed | Dynamic, duck typed |
| Async/Await | Native support throughout | Available but not used here |
| Null Safety | Nullable reference types | None by default |
| Records | Native record types | dataclass decorator |
| Extension Methods | Yes | No (use functions) |
| Properties | Auto-properties | @property decorator |

### Web Frameworks

| Aspect | ASP.NET Core | Flask |
|--------|--------------|-------|
| Style | Minimal APIs, Route registration | Decorators |
| DI | Built-in container | Manual or use Flask extensions |
| Configuration | IOptions pattern | Environment variables |
| Middleware | Pipeline-based | @app.before_request, etc. |
| Model Binding | Automatic | Manual (request.files, etc.) |

### Image Processing

| Library | C# - SkiaSharp | Python - Pillow |
|---------|----------------|-----------------|
| API Style | Object-oriented | Object-oriented |
| Drawing | Canvas + Paint objects | ImageDraw |
| Color | SKColors.Black | 'black' string or RGB tuple |
| Format | Enum (SKEncodedImageFormat) | String ('PNG') |

### Package Management

| Aspect | C# - NuGet | Python - pip |
|--------|------------|--------------|
| Config File | .csproj | requirements.txt |
| Install | dotnet restore | pip install -r requirements.txt |
| Virtual Env | Not needed | venv recommended |

### Configuration

| Aspect | C# | Python |
|--------|-----|--------|
| Storage | appsettings.json | .env file |
| Access | IOptions<T> | os.getenv() |
| Validation | Data Annotations | Manual validation |
| Binding | Automatic section binding | Manual env var reading |

## Performance Considerations

### C#
- Compiled language (faster execution)
- Async/await throughout (better for I/O)
- Smaller memory footprint
- Better for high-traffic scenarios

### Python
- Interpreted language (slower execution)
- Synchronous in this implementation
- Higher memory usage
- Can use async Flask or FastAPI for better performance
- Can scale horizontally with multiple workers

## When to Use Which

### Use C# Version When:
- You have a .NET infrastructure
- You need high performance
- You want strong typing
- You have C# developers
- You need enterprise features

### Use Python Version When:
- You have Python infrastructure
- You need rapid development
- You prefer dynamic typing
- You have Python developers
- You want simpler deployment
- You're integrating with Python ML/AI tools

## Migration Notes

If converting code between languages:

1. **Async → Sync**: Python version is synchronous; Azure SDKs still work
2. **DI → Factory**: Use factory functions instead of DI container
3. **Records → Dataclasses**: Use @dataclass for simple data objects
4. **IOptions → Config class**: Use static class with os.getenv()
5. **Extension methods → Functions**: Convert to standalone functions
6. **LINQ → List comprehensions**: Use Python's built-in iteration

## Testing Comparison

**C# Testing (xUnit example)**
```csharp
[Fact]
public async Task RedactPii_ShouldReturnImage()
{
    // Arrange
    var service = new PiiRedactionService(...);
    var imageBytes = File.ReadAllBytes("test.png");
    
    // Act
    var result = await service.RedactPii(imageBytes);
    
    // Assert
    Assert.NotNull(result);
    Assert.Equal("image/png", result.ContentType);
}
```

**Python Testing (pytest example)**
```python
def test_redact_pii_returns_image():
    # Arrange
    service = PiiRedactionService(...)
    with open("test.png", "rb") as f:
        image_bytes = f.read()
    
    # Act
    content, content_type = service.redact_pii(image_bytes)
    
    # Assert
    assert content is not None
    assert content_type == "image/png"
```

## Conclusion

Both versions provide the same functionality with similar architecture. The choice depends on your:
- Existing infrastructure
- Team expertise
- Performance requirements
- Integration needs
- Deployment environment

The Python version is more accessible for rapid prototyping and data science workflows, while the C# version offers better performance for high-traffic production scenarios.
