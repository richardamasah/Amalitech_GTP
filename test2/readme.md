# AWS S3 Data Lake Setup Report

## Executive Summary

This report details the successful implementation of an Amazon S3-based data lake using the bucket **`data-lake75`**. The setup follows best practices for **security**, **scalability**, and **cost optimization**, including:

- Bucket versioning
- SSE-S3 encryption
- Lifecycle policies
- IAM-based access control

The data lake stores structured data files (`people.csv`, `people1.csv`, `flights_details.csv`) and supports **serverless querying via AWS Athena** (`dj_table` database) and **S3 Select**, offering a scalable and cost-effective foundation for enterprise analytics.

---

## Introduction

Amazon S3 is an ideal platform for building data lakes due to its high durability, scalability, and integration with analytics services. This README outlines the setup of the `data-lake75` bucket for secure structured data storage and efficient querying, based on a hands-on lab exercise.

---

## Step-by-Step Implementation

### Step 1: Creating the S3 Bucket

- **Bucket Name:** `data-lake75`  
- **Region:** `us-east-1`  
- **Versioning:** Enabled  

Versioning was enabled to ensure data integrity and recoverability.

---

### Step 2: Configuring Bucket Policies and Permissions

All public access was blocked. The following IAM policy was used to allow controlled access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::data-lake75",
        "arn:aws:s3:::data-lake75/*"
      ]
    }
  ]
}

Step 3: Enabling Encryption
Encryption Type: SSE-S3

Status: Enabled

All objects are automatically encrypted at rest using S3-managed keys.

Step 4: Defining Lifecycle Policies
Two lifecycle rules were applied:

Transition to Glacier: After 90 days for cost-effective storage.

Delete non-current versions: After 365 days to manage storage growth.

Querying Data with AWS Athena
A database named dj_table was created. Athena was granted access with the following policy:

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::data-lake75",
        "arn:aws:s3:::data-lake75/*"
      ]
    }
  ]
}

Cost Analysis
Service	Cost Estimate
S3 Standard	~$0.023/GB/month (active data)
S3 Glacier	~$0.004/GB/month (archived data)
Versioning	Minimal (non-current versions)
SSE-S3 Encryption	Free
Athena	~$5.00/TB scanned
S3 Select	~$0.0007 per 1000 requests