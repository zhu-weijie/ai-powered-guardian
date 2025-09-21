### **Project Requirement Document (PRD): AI-Powered Guardian**

*   **Version:** v1.0.0
*   **Date:** 2025-09-21

#### **1. Introduction & Business Objectives**

This document outlines the requirements for the **AI-Powered Guardian**, a sophisticated Role-Based Access Control (RBAC) system designed for the asset management division of a bank.

The primary goal is to create a secure, intelligent, and efficient platform for managing access to sensitive financial assets. This system will replace static, manual access control processes with a dynamic, automated, and auditable framework. It is built on a modern, cloud-native architecture using FastAPI, React, and a suite of managed AWS services to ensure security, scalability, and reliability.

**Business Objectives:**

*   **Enhance Security:** Drastically reduce the risk of unauthorized access through fine-grained RBAC, Just-in-Time (JIT) permissions, and centralized secrets management.
*   **Improve Operational Efficiency:** Automate the user lifecycle via HRIS integration and provide a streamlined web interface for administrators, reducing manual overhead.
*   **Strengthen Regulatory Compliance:** Ensure a complete, immutable audit trail of all access-related activities and provide a mechanism to stream security events to the bank's SIEM platform.
*   **Enable Proactive Threat Detection:** Leverage a machine learning model to analyze access patterns in real-time, identify anomalous behavior, and provide risk scores to inform access decisions.


#### **2. Scope**

**2.1. In Scope:**
*   The design, development, and deployment of a cloud-native access control system.
*   Secure management of user identities, roles, and permissions.
*   A web-based administrative interface for system management.
*   An automated, real-time pipeline for AI-driven risk scoring of access requests.
*   An offline MLOps pipeline for retraining the AI model.
*   Integration with an external HRIS for identity lifecycle management.
*   Integration with an external SIEM for security event forwarding.
*   Just-in-Time (JIT) access request and approval workflows.

**2.2. Out of Scope:**
*   The management of the financial assets themselves.
*   A mobile application for administration.
*   Direct end-user (bank customer) access to the system.
*   The implementation of the external HRIS or SIEM platforms.

#### **3. Functional Requirements (FRs) - Refined**

**FR1: Identity and Authentication**
*   **FR1.1:** The system must allow new users to be created via the HRIS sync or a secure administrative endpoint.
*   **FR1.2:** Users must authenticate using their email and a password. Passwords must adhere to NIST 800-63B complexity and length requirements.
*   **FR1.3:** Upon successful login, the system must return a signed JWT (using HS256 algorithm) with a configurable expiration (default: 30 minutes).
*   **FR1.4:** A secure password reset mechanism must be available for administrators to trigger.

**FR2: Automated User Lifecycle Management**
*   **FR2.1:** The system must connect to the bank's HRIS via a secure API (or SCIM protocol if available) to synchronize user records.
*   **FR2.2:** The sync process must run on a configurable schedule (e.g., every 15 minutes) and must correctly handle new hires (provision), role changes (update), and terminations (deactivate).

**FR3: Role-Based Access Control (RBAC)**
*   **FR3.1:** Administrators must have access to protected API endpoints to perform Create, Read, Update, and Delete (CRUD) operations on roles and user-role assignments.
*   **FR3.2:** Any change to a role's permissions or a user's role assignment **must** be recorded as a high-priority event in the audit log.

**FR4: Just-in-Time (JIT) Access & Approvals**
*   **FR4.1:** Users must be able to request temporary access to a role for a configurable duration, with a system-defined maximum limit (e.g., 8 hours).
*   **FR4.2:** The system must send a notification (e.g., email) to a pre-defined approver.
*   **FR4.3:** The entire lifecycle of a JIT request (request, approval/denial, grant, automatic revocation) must be captured as a single, correlated event in the audit log.

**FR5: AI-Powered Anomaly Detection**
*   **FR5.1:** For designated high-impact operations, the system must send the request context (e.g., User ID, Asset Sensitivity, Time of Day, IP Geolocation) to the AI service for real-time risk scoring.
*   **FR5.2:** The AI service must return a risk score (e.g., 0-100).
*   **FR5.3 (AI Explainability - XAI):** For any risk score exceeding a "high" threshold, the AI service must provide the top 3 contributing factors to that score (e.g., "Unusual time of day," "High-sensitivity asset"). This reason must be included in the audit log.

**FR6: Auditing and SIEM Integration**
*   **FR6.1:** All security-sensitive events must be logged asynchronously to a dedicated, immutable audit database.
*   **FR6.2:** The system must provide a reliable, streaming data pipeline to forward all audit events to the bank's SIEM in **Common Event Format (CEF)** or structured JSON within **5 minutes** of the event occurring.

**FR7: Administration User Interface**
*   **FR7.1:** The system must provide a secure, responsive web-based SPA.
*   **FR7.2:** All data tables (e.g., Users, Roles) must support pagination, searching, and filtering.
*   **FR7.3:** The UI must provide intuitive forms and modals for creating and editing resources.

#### **4. Non-Functional Requirements (NFRs) - Refined**

**NFR1: Security**
*   **NFR1.1:** All application secrets must be managed via AWS Secrets Manager, with support for automatic credential rotation for the RDS databases.
*   **NFR1.2:** The system must undergo quarterly automated vulnerability scans and annual third-party penetration tests. Critical vulnerabilities must be patched within **15 days**; High vulnerabilities within **30 days**.
*   **NFR1.3:** All network traffic must be within a private VPC, with no backend services exposed directly to the public internet. Communication with external AWS services must use private VPC Endpoints.

**NFR2: Availability & Disaster Recovery**
*   **NFR2.1:** The system must achieve a minimum uptime of **99.95%**, calculated monthly.
*   **NFR2.2 (Disaster Recovery):** The system must be deployable across multiple Availability Zones with a documented disaster recovery plan that meets the following objectives:
    *   **Recovery Time Objective (RTO):** < 4 hours.
    *   **Recovery Point Objective (RPO):** < 15 minutes.

**NFR3: Performance and Scalability**
*   **NFR3.1 (Latency):** 99% of all real-time access authorization decisions (including AI risk scoring) must be completed in **under 200 milliseconds**.
*   **NFR3.2 (Concurrent Load):** The system must support **5,000 concurrent active users** making an average of 10 requests per minute without performance degradation.
*   **NFR3.3 (Scalability):** All compute services must be configured to auto-scale horizontally based on CPU and memory utilization, with a scaling trigger at 75% utilization.

**NFR4: Maintainability and Operations**
*   **NFR4.1 (Infrastructure as Code):** All cloud infrastructure must be defined and managed as code using Terraform.
*   **NFR4.2 (Migrations):** All database schema changes must be managed via Alembic and reviewed as part of the code review process. Manual schema changes are forbidden.
*   **NFR4.3 (Observability):** All services must output structured (JSON) logs to Amazon CloudWatch. A set of pre-defined dashboards and alarms must be created to monitor key health metrics (e.g., latency, error rates, queue depth).

**NFR5: MLOps & AI Governance**
*   **NFR5.1:** The MLOps retraining pipeline must run on an automated schedule (e.g., weekly).
*   **NFR5.2 (Model Governance):** The pipeline must include an automated evaluation step. A new model version will only be approved for deployment if its accuracy exceeds the currently deployed model by a pre-defined threshold (e.g., 5%).
*   **NFR5.3 (Bias Monitoring):** The pipeline must generate a report to monitor for model bias across key user attributes (e.g., role, department) to ensure fairness.

**NFR6: Usability**
*   **NFR6.1:** Administrative workflows in the UI must be intuitive and require minimal training.
*   **NFR6.2:** The UI must be responsive and fully functional on modern web browsers (Chrome, Firefox, Edge).

#### **5. Glossary**
*   **JIT:** Just-in-Time Access
*   **MLOps:** Machine Learning Operations
*   **PRD:** Project Requirement Document
*   **RPO:** Recovery Point Objective - The maximum acceptable amount of data loss.
*   **RTO:** Recovery Time Objective - The maximum acceptable downtime in a disaster.
*   **SIEM:** Security Information and Event Management
*   **XAI:** Explainable Artificial Intelligence
