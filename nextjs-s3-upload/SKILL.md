---
name: nextjs-s3-upload
description: >
  Complete guide for integrating AWS S3 file uploads into Next.js (App Router) applications using
  presigned URLs. Use this skill whenever the user wants to upload files, images, videos, or
  documents to S3 from a Next.js app — even if they just say "add file upload", "store files in S3",
  "upload images to AWS", "S3 bucket integration", or "handle user uploads". Covers: S3 bucket setup
  and CORS configuration, IAM permissions, environment variables, Route Handler for presigned URL
  generation, client-side upload component with progress tracking, TypeScript-first patterns,
  file-type/size validation, and common error fixes. Also handles S3-compatible services (Cloudflare
  R2, MinIO, DigitalOcean Spaces).
---

# Next.js S3 Upload Skill

A complete, production-ready integration of AWS S3 file uploads into a Next.js App Router project
using presigned URLs. Follow the steps in order — each builds on the previous.

---

## How It Works (Architecture)

```
Client → POST /api/upload-url (Next.js Route Handler) → AWS SDK generates presigned URL
Client → PUT <presigned URL> (directly to S3, no server involved) → File lands in S3
```

Why presigned URLs?
- **Secure** — AWS credentials never reach the client
- **Fast** — Files upload directly to S3; your server handles zero bytes
- **Scalable** — No memory/bandwidth limits from your own server
- **Flexible** — Works on Vercel, Railway, any serverless host

---

## Step 1 — AWS Setup

### Create S3 Bucket
1. Go to **AWS Console → S3 → Create bucket**
2. Enter a bucket name (e.g., `my-app-uploads`)
3. Select your region (note it — you'll need it)
4. Under **Object Ownership** → select **ACLs enabled** → **Bucket owner preferred**
5. **Block Public Access**: Uncheck all if files should be publicly readable; otherwise leave blocked
6. Click **Create bucket**

### Configure CORS (required for browser uploads)
In your bucket → **Permissions** → **Cross-origin resource sharing (CORS)** → Edit:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

> For production, replace `"*"` in `AllowedOrigins` with your actual domain(s).

### Create IAM User with Minimal Permissions
1. **IAM → Users → Create user** (e.g., `my-app-s3-user`)
2. **Attach policies directly** → Create inline policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::YOUR-BUCKET-NAME",
        "arn:aws:s3:::YOUR-BUCKET-NAME/*"
      ]
    }
  ]
}
```

3. After creating the user → **Security credentials → Create access key** → Application running outside AWS
4. Copy **Access key ID** and **Secret access key**

---

## Step 2 — Environment Variables

Add to `.env.local` (never commit this file):

```env
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
S3_BUCKET_NAME=my-app-uploads
```

> The variable names `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION` are the AWS SDK
> defaults — the SDK picks them up automatically without manual credential passing.

---

## Step 3 — Install Dependencies

```bash
npm install @aws-sdk/client-s3 @aws-sdk/s3-request-presigner
```

---

## Step 4 — S3 Client Singleton

Create `lib/s3.ts` (shared across route handlers):

```typescript
// lib/s3.ts
import { S3Client } from "@aws-sdk/client-s3";

// Singleton — avoids creating a new client on every request in development
const s3 = new S3Client({
  region: process.env.AWS_REGION!,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});

export default s3;
```

---

## Step 5 — Route Handler (Presigned URL Generator)

Create `app/api/upload-url/route.ts`:

```typescript
// app/api/upload-url/route.ts
import { NextRequest, NextResponse } from "next/server";
import { PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import { randomUUID } from "crypto";
import s3 from "@/lib/s3";

// Allowed MIME types — customize for your use case
const ALLOWED_TYPES = [
  "image/jpeg",
  "image/png",
  "image/webp",
  "image/gif",
  "application/pdf",
  "video/mp4",
];

// 10 MB limit
const MAX_FILE_SIZE = 10 * 1024 * 1024;

export async function POST(request: NextRequest) {
  try {
    const { fileName, fileType, fileSize } = await request.json();

    // --- Validation ---
    if (!fileName || !fileType || !fileSize) {
      return NextResponse.json(
        { error: "fileName, fileType, and fileSize are required" },
        { status: 400 }
      );
    }

    if (!ALLOWED_TYPES.includes(fileType)) {
      return NextResponse.json(
        { error: `File type ${fileType} is not allowed` },
        { status: 400 }
      );
    }

    if (fileSize > MAX_FILE_SIZE) {
      return NextResponse.json(
        { error: "File size exceeds 10 MB limit" },
        { status: 400 }
      );
    }

    // --- Generate a unique key to avoid filename collisions ---
    const extension = fileName.split(".").pop();
    const key = `uploads/${randomUUID()}.${extension}`;

    const command = new PutObjectCommand({
      Bucket: process.env.S3_BUCKET_NAME!,
      Key: key,
      ContentType: fileType,
      ContentLength: fileSize,
    });

    // URL is valid for 60 seconds
    const presignedUrl = await getSignedUrl(s3, command, { expiresIn: 60 });

    // The public URL the file will be accessible at after upload
    const publicUrl = `https://${process.env.S3_BUCKET_NAME}.s3.${process.env.AWS_REGION}.amazonaws.com/${key}`;

    return NextResponse.json({ presignedUrl, key, publicUrl });
  } catch (error) {
    console.error("Error generating presigned URL:", error);
    return NextResponse.json(
      { error: "Failed to generate upload URL" },
      { status: 500 }
    );
  }
}
```

---

## Step 6 — Upload Hook (Client-Side)

Create `hooks/useS3Upload.ts` for reusable upload logic with progress tracking:

```typescript
// hooks/useS3Upload.ts
"use client";
import { useState } from "react";

interface UploadResult {
  key: string;
  publicUrl: string;
}

interface UploadState {
  progress: number;       // 0–100
  isUploading: boolean;
  error: string | null;
  result: UploadResult | null;
}

export function useS3Upload() {
  const [state, setState] = useState<UploadState>({
    progress: 0,
    isUploading: false,
    error: null,
    result: null,
  });

  const upload = async (file: File): Promise<UploadResult | null> => {
    setState({ progress: 0, isUploading: true, error: null, result: null });

    try {
      // 1. Get presigned URL from our Route Handler
      const res = await fetch("/api/upload-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fileName: file.name,
          fileType: file.type,
          fileSize: file.size,
        }),
      });

      if (!res.ok) {
        const { error } = await res.json();
        throw new Error(error || "Failed to get upload URL");
      }

      const { presignedUrl, key, publicUrl } = await res.json();

      // 2. Upload directly to S3 using XMLHttpRequest (supports progress events)
      await new Promise<void>((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            const percent = Math.round((event.loaded / event.total) * 100);
            setState((prev) => ({ ...prev, progress: percent }));
          }
        };

        xhr.onload = () => {
          if (xhr.status === 200) resolve();
          else reject(new Error(`S3 upload failed with status ${xhr.status}`));
        };

        xhr.onerror = () => reject(new Error("Network error during upload"));

        xhr.open("PUT", presignedUrl);
        xhr.setRequestHeader("Content-Type", file.type);
        xhr.send(file);
      });

      const result = { key, publicUrl };
      setState({ progress: 100, isUploading: false, error: null, result });
      return result;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Upload failed";
      setState({ progress: 0, isUploading: false, error: message, result: null });
      return null;
    }
  };

  const reset = () =>
    setState({ progress: 0, isUploading: false, error: null, result: null });

  return { ...state, upload, reset };
}
```

---

## Step 7 — Upload Component

Create `components/FileUpload.tsx`:

```tsx
// components/FileUpload.tsx
"use client";
import { useRef } from "react";
import { useS3Upload } from "@/hooks/useS3Upload";

export function FileUpload() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { upload, progress, isUploading, error, result, reset } = useS3Upload();

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    await upload(file);
  };

  return (
    <div className="flex flex-col gap-4 p-6 border rounded-lg max-w-md">
      <h2 className="font-semibold text-lg">Upload File</h2>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*,application/pdf,video/mp4"
        onChange={handleFileChange}
        disabled={isUploading}
        className="hidden"
      />

      <button
        onClick={() => { reset(); fileInputRef.current?.click(); }}
        disabled={isUploading}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {isUploading ? `Uploading… ${progress}%` : "Choose File"}
      </button>

      {isUploading && (
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      {error && (
        <p className="text-red-500 text-sm">Error: {error}</p>
      )}

      {result && (
        <div className="text-sm text-green-700">
          <p>✅ Upload complete!</p>
          <a
            href={result.publicUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="underline break-all"
          >
            {result.publicUrl}
          </a>
        </div>
      )}
    </div>
  );
}
```

---

## File Structure

```
app/
  api/
    upload-url/
      route.ts        ← presigned URL generator
components/
  FileUpload.tsx      ← drop-in upload UI
hooks/
  useS3Upload.ts      ← upload logic + progress
lib/
  s3.ts               ← S3 client singleton
.env.local            ← AWS credentials (never commit)
```

---

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `403 Forbidden` on PUT | Wrong IAM permissions | Ensure `s3:PutObject` is allowed in IAM policy |
| `CORS error` on PUT | Missing CORS config on bucket | Add CORS JSON from Step 1 |
| `AccessDenied` | Wrong region or credentials | Double-check `.env.local` values |
| `SignatureDoesNotMatch` | Clock skew or whitespace in key | Check for accidental whitespace in env vars |
| `NoSuchBucket` | Wrong bucket name | Verify `S3_BUCKET_NAME` env var |
| Presigned URL expired | Client too slow or long queue | Increase `expiresIn` in `getSignedUrl` call |

---

## Variants & Enhancements

For advanced use cases, read the reference files:

- **`references/server-action.md`** — Using Next.js Server Actions instead of a Route Handler (simpler, no `fetch` call needed)
- **`references/s3-compatible.md`** — Connecting to Cloudflare R2, MinIO, or DigitalOcean Spaces
- **`references/multipart.md`** — Multipart upload for files >5 GB
- **`references/delete.md`** — Deleting objects from S3

---

## Quick Checklist Before Testing

- [ ] S3 bucket created with CORS configured
- [ ] IAM user created with `s3:PutObject` permission on the bucket
- [ ] `.env.local` has all 4 variables (KEY, SECRET, REGION, BUCKET)
- [ ] AWS SDK packages installed
- [ ] `lib/s3.ts`, `app/api/upload-url/route.ts`, `hooks/useS3Upload.ts`, `components/FileUpload.tsx` all created
- [ ] `<FileUpload />` imported and used somewhere in your app
