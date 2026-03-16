# S3-Compatible Services (R2, MinIO, DigitalOcean Spaces)

The same code works with any S3-compatible API — just change the `endpoint` in the S3Client config
and adjust the public URL format.

## Cloudflare R2

R2 has no egress fees and a generous free tier. The API is fully S3-compatible.

```typescript
// lib/s3.ts (R2 version)
import { S3Client } from "@aws-sdk/client-s3";

const s3 = new S3Client({
  region: "auto",
  endpoint: `https://${process.env.CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com`,
  credentials: {
    accessKeyId: process.env.R2_ACCESS_KEY_ID!,
    secretAccessKey: process.env.R2_SECRET_ACCESS_KEY!,
  },
});

export default s3;
```

```env
# .env.local for R2
CLOUDFLARE_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
S3_BUCKET_NAME=your-r2-bucket
```

Public URL format (if you've set up a custom domain or R2 public bucket):
```
https://pub-<hash>.r2.dev/<key>
```

---

## MinIO (Self-Hosted)

```typescript
// lib/s3.ts (MinIO version)
import { S3Client } from "@aws-sdk/client-s3";

const s3 = new S3Client({
  region: "us-east-1", // MinIO doesn't use real regions, but this field is required
  endpoint: process.env.MINIO_ENDPOINT!, // e.g. http://localhost:9000
  forcePathStyle: true, // Required for MinIO
  credentials: {
    accessKeyId: process.env.MINIO_ACCESS_KEY!,
    secretAccessKey: process.env.MINIO_SECRET_KEY!,
  },
});

export default s3;
```

```env
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
S3_BUCKET_NAME=uploads
```

---

## DigitalOcean Spaces

```typescript
// lib/s3.ts (Spaces version)
import { S3Client } from "@aws-sdk/client-s3";

const s3 = new S3Client({
  region: process.env.DO_SPACES_REGION!, // e.g. nyc3
  endpoint: `https://${process.env.DO_SPACES_REGION}.digitaloceanspaces.com`,
  credentials: {
    accessKeyId: process.env.DO_SPACES_KEY!,
    secretAccessKey: process.env.DO_SPACES_SECRET!,
  },
});

export default s3;
```

```env
DO_SPACES_REGION=nyc3
DO_SPACES_KEY=your_spaces_key
DO_SPACES_SECRET=your_spaces_secret
S3_BUCKET_NAME=your-space-name
```

Public URL format:
```
https://<bucket>.nyc3.digitaloceanspaces.com/<key>
```

---

## Route Handler Stays the Same

With any of the above clients, `app/api/upload-url/route.ts` and `hooks/useS3Upload.ts` from
the main SKILL.md need **no changes**. Only `lib/s3.ts` and `.env.local` differ.
