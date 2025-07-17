## **Canvas LMS - Rich Content Editor (RCE) Setup Instructions**

This document outlines the process used to get the Rich Content Editor (RCE) running for a self-hosted Canvas LMS installation. Instructre's guide is helpful to get started, [RCE](https://github.com/instructure/canvas-rce-api/blob/master/README.md). 

---

### **1.**

### **Domain and SSL Configuration**

- Configure subdomains:
  
  - rce.example.edu
  
  - files.example.edu

- Point both to your Canvas LMS host.

- Install valid SSL certificates for each domain (PEM, KEY, and CHAIN files).

- Configure Apache to use these certificates.

---

### **2.**

### **Deploy RCE via Docker**

- Use the official Instructure RCE Docker image, e.g., instructure/canvas-rce-api.

- Set environment variables when launching the container:

```
CANVAS_DOMAIN=https://rce.example.edu
CANVAS_LMS_DOMAIN=https://canvas.example.edu
RCE_SECRET=<your-secret>
RCE_SIGNATURE_SECRET=<your-signature-secret>
```

- Be sure that the secrets match those in /var/canvas/config/vault_secrets.yml

- Expose port 3001 (or other internal port) for Apache to reverse proxy.

---

### **3.**

### **Apache Reverse Proxy Configuration**

Create a virtual host entry for the RCE domain:

```
<VirtualHost *:443>
  ServerName rce.example.edu

  SSLEngine on
  SSLCertificateFile /path/to/fullchain.pem
  SSLCertificateKeyFile /path/to/privkey.pem

  ProxyPreserveHost On
  ProxyPass / http://localhost:3001/
  ProxyPassReverse / http://localhost:3001/
</VirtualHost>
```

---

### **4.**

### **Canvas LMS Settings (Rails Console)**

Run the following in the Canvas Rails console:

```
Setting.set('rich_content_service_url', 'https://rce.example.edu')
Setting.set('rich_content_service_access_token', '<your-access-token>')
```

Confirm the following:

- Canvas is running in production mode

- Background jobs are active (canvas-jobs.service)

- File store is working

- InstFS is enabled if using file uploads

---

### **5.**

### **Verification**

- Open a course and create/edit content using the RCE.

- Ensure the editor loads and functions correctly.

- Check browser console and logs for errors.

---

Document generated: 2025-07-17

Maintainer: Nicholas Hadley
