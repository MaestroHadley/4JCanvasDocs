## **Self-Hosted Canvas LMS: Required Modifications & Fixes**

This document outlines all key changes and workarounds made to our Canvas LMS instance to ensure successful installation, functionality, and course export/import. Each section lists the change and relevant context.

---

### **1.**

### **Set Environment to Production**

- **Issue**: Canvas defaulted to development mode.

- **Fix**:
  
  - Updated the systemd service files (canvas.service, canvas-jobs.service) to include:

```
Environment=RAILS_ENV=production
```

- - 
  
  - Also added to the ExecStart command as:

```
ExecStart=/bin/bash -lc 'RAILS_ENV=production bundle exec script/canvas_init run'
```

---

### **2.**

### **Fixing the File Storage Location**

- **Issue**: Canvas exported files were not being saved or downloadable.

- **Root Cause**: Exports and uploads were being sent to the tmp directory

```
/var/canvas/tmp
```

- **Fix**: Set correct file store location in config/file_store.yml:

```
production:
  storage: local
  path_prefix: public/files
```

- **Also**: Verified directory ownership by canvasuser, ensured Passenger/Apache had access.

---

### **3.**

### **Patch for Content Export Attachment Handling**

- **Issue**: Export file would not attach and Canvas refused to overwrite or create a new one, causing course copy and export to fail silently.

- **Fix**: Inserted methods to locate and destroy existing export attachments before generating a new one. This ensures a fresh attachment is always created during export.

- **Patch** (inserted near the end of /var/canvas/app/models/content_export.rb, above the private section):

```
def export!
  clean_existing_export_attachment!
  super
end

def clean_existing_export_attachment!
  return unless context && user
  previous_attachment = Attachment
    .where(user_id: user.id, context_id: context.id, display_name: "#{context.name.parameterize}-export.imscc")
    .order(created_at: :desc)
    .first

  previous_attachment&.destroy
end

def self.find_existing_export(*args)
  return nil
end
```

---

### **4.**

### **Fixed Improper CSRF Token Calls to Instructure**

- **Issue**: Canvas attempted to hit canvas.instructure.com for CSRF tokens.

- **Fix**:
  
  - Found and removed outdated or default references in config files (likely leftover config or gem defaults).
  
  - Verified all domain references in:

```
grep -ri 'domain' /var/canvas/config
```

- Cleared cookies/cache; restarted Apache and background jobs.

---

### **5.**

### **Enable Temp File Cleanup and Access**

- **Issue**: Canvas-generated export files were not being cleaned or accessible.

- **Fixes**:
  
  - Located files in /tmp or /var/canvas/tmp; used tree and find to debug.
  
  - Ensured delayed jobs were enabled and working with canvas-jobs.service.
  
  - Set correct permissions to allow Attachment system to read/write tmp files.

---

### **6.**

### **Service File: canvas-jobs.service**

- **User**: canvasuser

- **Key Config**:

```
[Unit]
Description=Canvas LMS Background Jobs

[Service]
Type=simple
User=canvasuser
WorkingDirectory=/var/canvas
ExecStart=/bin/bash -lc 'RAILS_ENV=production bundle exec script/delayed_job start'
Restart=always
Environment=RAILS_ENV=production

[Install]
WantedBy=multi-user.target
```

It is crucial that the ExecStart be set to the delayed_jobs script. Some of the config files and instructions online do not state this, or incorrectly point to canvas_init. 



---

### **7.**

### **Other Notes**

- Ensure all gems are installed as canvasuser and not root.

- Be cautious of conflicting .env or environment variables.

- Always use Setting.set in Rails console for persistent config:

```
Setting.set("some_setting", "value")
```

---

Document generated: 2025-07-17

Maintainer: Nicholas Hadley
