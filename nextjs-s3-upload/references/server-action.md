# S3 Upload via Next.js Server Actions

Use this when you want to avoid a separate `fetch()` call and keep everything in one Server Action.
Works great for form-based uploads.

## When to Use
- You're already using Server Actions for forms
- You want simpler client code (no manual `fetch` to `/api/upload-url`)
- You're okay with the tradeoff: no upload progress bar (fetch doesn't support it natively in Server Actions)

## Installation

```bash
npm install @aws-sdk/client-s3 @aws-sdk/s3-request-presigner
```

## Server Action

```typescript
// app/actions/upload.ts
"use server";
import { PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import { randomUUID } from "crypto";
import s3 from "@/lib/s3";

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp", "application/pdf"];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

export async function getPresignedUploadUrl(formData: FormData) {
  const file = formData.get("file") as File;

  if (!file) throw new Error("No file provided");
  if (!ALLOWED_TYPES.includes(file.type)) throw new Error("File type not allowed");
  if (file.size > MAX_FILE_SIZE) throw new Error("File too large");

  const extension = file.name.split(".").pop();
  const key = `uploads/${randomUUID()}.${extension}`;

  const command = new PutObjectCommand({
    Bucket: process.env.S3_BUCKET_NAME!,
    Key: key,
    ContentType: file.type,
    ContentLength: file.size,
  });

  const presignedUrl = await getSignedUrl(s3, command, { expiresIn: 60 });
  const publicUrl = `https://${process.env.S3_BUCKET_NAME}.s3.${process.env.AWS_REGION}.amazonaws.com/${key}`;

  return { presignedUrl, key, publicUrl };
}
```

## Client Component

```tsx
// components/FileUploadAction.tsx
"use client";
import { useState } from "react";
import { getPresignedUploadUrl } from "@/app/actions/upload";

export function FileUploadAction() {
  const [status, setStatus] = useState<"idle" | "uploading" | "done" | "error">("idle");
  const [publicUrl, setPublicUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const file = formData.get("file") as File;
    if (!file) return;

    setStatus("uploading");
    setError(null);

    try {
      // 1. Call Server Action to get presigned URL
      const { presignedUrl, publicUrl } = await getPresignedUploadUrl(formData);

      // 2. Upload directly to S3
      const res = await fetch(presignedUrl, {
        method: "PUT",
        body: file,
        headers: { "Content-Type": file.type },
      });

      if (!res.ok) throw new Error("S3 upload failed");

      setPublicUrl(publicUrl);
      setStatus("done");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
      setStatus("error");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <input type="file" name="file" accept="image/*,application/pdf" required />
      <button type="submit" disabled={status === "uploading"}>
        {status === "uploading" ? "Uploading..." : "Upload"}
      </button>
      {status === "done" && <a href={publicUrl!} target="_blank">View file ↗</a>}
      {error && <p className="text-red-500">{error}</p>}
    </form>
  );
}
```

## Key Difference from Route Handler Approach

| | Route Handler | Server Action |
|---|---|---|
| Progress tracking | ✅ XHR supports it | ❌ Not without workarounds |
| Code simplicity | Moderate | Simpler client code |
| File size limit | Limited by Route Handler body | Still limited by Next.js body parser |
| Reusability | Easy to call from anywhere | Tied to React component tree |
