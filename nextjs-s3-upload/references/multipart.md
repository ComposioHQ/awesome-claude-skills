# Multipart Upload for Large Files (>100 MB)

For files larger than ~100 MB (and required for anything over 5 GB), S3's Multipart Upload API
splits the file into parts, uploads them in parallel, then S3 reassembles them.

S3 multipart limits:
- Minimum part size: **5 MB** (except the last part)
- Maximum parts: **10,000**
- Maximum file size: **5 TB**

## Install additional package

```bash
npm install @aws-sdk/lib-storage
```

## Route Handler — Multipart via @aws-sdk/lib-storage (Recommended)

The `@aws-sdk/lib-storage` `Upload` class handles chunking and retry automatically.
Because it streams directly from the server, use this in a **Route Handler**, not a Server Action
(Server Actions buffer the entire body).

```typescript
// app/api/upload-multipart/route.ts
import { NextRequest, NextResponse } from "next/server";
import { Upload } from "@aws-sdk/lib-storage";
import s3 from "@/lib/s3";

export const runtime = "nodejs"; // Edge runtime doesn't support streams well here

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get("file") as File;

    if (!file) {
      return NextResponse.json({ error: "No file provided" }, { status: 400 });
    }

    const extension = file.name.split(".").pop();
    const key = `uploads/${crypto.randomUUID()}.${extension}`;

    const upload = new Upload({
      client: s3,
      params: {
        Bucket: process.env.S3_BUCKET_NAME!,
        Key: key,
        Body: file.stream(),
        ContentType: file.type,
      },
      queueSize: 4,        // parallel upload threads
      partSize: 5 * 1024 * 1024, // 5 MB per part (minimum)
      leavePartsOnError: false,
    });

    await upload.done();

    const publicUrl = `https://${process.env.S3_BUCKET_NAME}.s3.${process.env.AWS_REGION}.amazonaws.com/${key}`;
    return NextResponse.json({ key, publicUrl });
  } catch (error) {
    console.error("Multipart upload failed:", error);
    return NextResponse.json({ error: "Upload failed" }, { status: 500 });
  }
}
```

## Client — Upload with Progress

```typescript
// hooks/useMultipartUpload.ts
"use client";
import { useState } from "react";

export function useMultipartUpload() {
  const [progress, setProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const upload = async (file: File) => {
    setIsUploading(true);
    setError(null);
    setProgress(0);

    try {
      const formData = new FormData();
      formData.append("file", file);

      // Use XHR for progress tracking
      const result = await new Promise<{ key: string; publicUrl: string }>(
        (resolve, reject) => {
          const xhr = new XMLHttpRequest();

          xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
              setProgress(Math.round((e.loaded / e.total) * 100));
            }
          };

          xhr.onload = () => {
            if (xhr.status === 200) {
              resolve(JSON.parse(xhr.responseText));
            } else {
              reject(new Error(`Upload failed: ${xhr.status}`));
            }
          };

          xhr.onerror = () => reject(new Error("Network error"));

          xhr.open("POST", "/api/upload-multipart");
          xhr.send(formData);
        }
      );

      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Upload failed";
      setError(message);
      return null;
    } finally {
      setIsUploading(false);
    }
  };

  return { upload, progress, isUploading, error };
}
```

## Vercel Note

Vercel's default body size limit is **4.5 MB**. For larger files, you have two options:

1. **Use presigned URLs** (recommended) — client uploads directly to S3, bypassing Vercel entirely
2. **Enable Vercel Pro/Enterprise** with `export const config = { api: { bodyParser: { sizeLimit: '50mb' } } }` — but this still hits memory limits

For files over ~10 MB on Vercel, **always use the presigned URL pattern** from the main skill,
not server-side streaming.
