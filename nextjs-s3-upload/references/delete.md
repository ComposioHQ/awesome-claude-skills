# Deleting Objects from S3

## Route Handler

```typescript
// app/api/delete-file/route.ts
import { NextRequest, NextResponse } from "next/server";
import { DeleteObjectCommand } from "@aws-sdk/client-s3";
import s3 from "@/lib/s3";

export async function DELETE(request: NextRequest) {
  try {
    const { key } = await request.json();

    if (!key) {
      return NextResponse.json({ error: "key is required" }, { status: 400 });
    }

    // Optional: validate the key belongs to the authenticated user
    // before deleting (important for multi-tenant apps)

    await s3.send(
      new DeleteObjectCommand({
        Bucket: process.env.S3_BUCKET_NAME!,
        Key: key,
      })
    );

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Delete failed:", error);
    return NextResponse.json({ error: "Failed to delete file" }, { status: 500 });
  }
}
```

## Client Usage

```typescript
async function deleteFile(key: string) {
  const res = await fetch("/api/delete-file", {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key }),
  });

  if (!res.ok) throw new Error("Delete failed");
  return res.json();
}
```

## Generating a Presigned Delete URL (if client needs to delete directly)

```typescript
import { DeleteObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import s3 from "@/lib/s3";

export async function getPresignedDeleteUrl(key: string) {
  const command = new DeleteObjectCommand({
    Bucket: process.env.S3_BUCKET_NAME!,
    Key: key,
  });

  return getSignedUrl(s3, command, { expiresIn: 60 });
}
```

## IAM Permission Required

Make sure your IAM policy includes:
```json
"s3:DeleteObject"
```
on `"arn:aws:s3:::YOUR-BUCKET-NAME/*"`.
