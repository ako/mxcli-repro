# File uploader

- **Widget ID:** `com.mendix.widget.web.fileuploader.FileUploader`
- **Type:** PLUGGABLEWIDGET
- **Version:** 2.2.2

## MDL Example

```sql
PLUGGABLEWIDGET 'com.mendix.widget.web.fileuploader.FileUploader' widget1 {
  allowedfileformat item1   -- one entry of `allowedFileFormats`
  custombutton item1   -- one entry of `customButtons`
}
```

## Properties

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `uploadMode` | enumeration | Yes | files |  |
| `associatedFiles` | datasource | Yes | FileUploader.FileUploadContext/FileUploader.UploadedFile_FileUploadContext/FileUploader.UploadedFile |  |
| `associatedImages` | datasource | Yes | FileUploader.FileUploadContext/FileUploader.UploadedImage_FileUploadContext/FileUploader.UploadedImage |  |
| `readOnlyMode` | boolean | Yes | false |  |
| `createFileAction` | action | Yes | FileUploader.ACT_CreateUploadedFileDocument | Nanoflow that creates a file object, associates it to the current object and ... |
| `createImageAction` | action | Yes | FileUploader.ACT_CreateUploadedImageDocument | Nanoflow that creates an image object, associates it to the current object an... |
| `allowedFileFormats` | object |  |  | No restrictions if left empty. |
| `maxFilesPerUpload` | integer | Yes | 10 | Limit the number of files per one upload. |
| `maxFileSize` | integer | Yes | 25 | Reject files that are bigger than specified size. |
| `dropzoneIdleMessage` | textTemplate | Yes |  |  |
| `dropzoneAcceptedMessage` | textTemplate | Yes |  |  |
| `dropzoneRejectedMessage` | textTemplate | Yes |  |  |
| `uploadInProgressMessage` | textTemplate | Yes |  |  |
| `uploadSuccessMessage` | textTemplate | Yes |  |  |
| `uploadFailureGenericMessage` | textTemplate | Yes |  |  |
| `uploadFailureInvalidFileFormatMessage` | textTemplate | Yes |  |  |
| `uploadFailureFileIsTooBigMessage` | textTemplate | Yes |  |  |
| `uploadFailureTooManyFilesMessage` | textTemplate | Yes |  |  |
| `unavailableCreateActionMessage` | textTemplate | Yes |  |  |
| `downloadButtonTextMessage` | textTemplate | Yes |  |  |
| `removeButtonTextMessage` | textTemplate | Yes |  |  |
| `removeSuccessMessage` | textTemplate | Yes |  |  |
| `removeErrorMessage` | textTemplate | Yes |  |  |
| `objectCreationTimeout` | integer | Yes | 10 | Consider uploads unsuccessful if the Action to create new files/images does n... |
| `enableCustomButtons` | boolean | Yes | false |  |
| `customButtons` | object |  |  |  |

## Object Lists (repeating child entries)

### `allowedfileformat` → property `allowedFileFormats`

Item properties:

| Property | Operation |
|----------|-----------|
| `configMode` | primitive |
| `predefinedType` | primitive |
| `mimeType` | primitive |
| `extensions` | primitive |
| `typeFormatDescription` | texttemplate |

### `custombutton` → property `customButtons`

Item properties:

| Property | Operation |
|----------|-----------|
| `buttonCaption` | texttemplate |
| `buttonActionFile` | action |
| `buttonActionImage` | action |
| `buttonIsDefault` | primitive |
| `buttonIsVisible` | expression |

