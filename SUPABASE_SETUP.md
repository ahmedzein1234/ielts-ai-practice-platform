
# Supabase Setup Guide

## Project Details
- Project ID: zzvskbvqtglzonftpikf
- Project Name: IELTS CURSOR
- URL: https://zzvskbvqtglzonftpikf.supabase.co

## Environment Variables
Create apps/web/.env.local with:
```
NEXT_PUBLIC_SUPABASE_URL=https://zzvskbvqtglzonftpikf.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
NEXT_PUBLIC_API_URL=https://ielts-api-gateway-production.up.railway.app
```

## Database Schema
Execute supabase/schema.sql in your Supabase SQL Editor

## Authentication
Configure site URL and redirect URLs in Supabase Auth settings

## Storage
Storage buckets are created automatically by the schema
