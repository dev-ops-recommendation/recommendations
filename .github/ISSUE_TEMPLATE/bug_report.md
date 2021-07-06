### Bug Report Example

### 500 Server Error (TypeError) if ContentType is not set (example)
If you send a request without setting the `ContentType` to `application/json` the app throws a TypeError when trying to validate the data.

### Steps to Reproduce
Send a `post/pets` to create a bew pet but not setting the `ContentType` in the header

### Expected Result
400 Bad Request

### Observed Result
500 Server Error
