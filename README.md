# Project 2 - Application Security Verification Standard (ASVS)

## Description

This project focuses on improving the security of an online merchandise store for the Department of Electronics, Telecommunications, and Informatics (DETI) at the University of Aveiro. The improvements align the application with the Level 1 requirements of the OWASP Application Security Verification Standard (ASVS). The primary goal was to audit the existing web application, identify security issues, and implement necessary enhancements without compromising the original functionality of the store.

The project includes two versions of the online store:
- **app_org**: The original version of the application.
- **app_sec**: The improved version with enhanced security features.

The key improvements made during this project include strengthening password security, implementing multi-factor authentication, enhancing input validation, improving session management, securing file uploads and downloads, and ensuring better management of sensitive data.

## Authors

- Francisco Gonçalves (nMec: 108538)

## Audited Issues and Implemented Improvements

1. **Password Strength Evaluation (V2.1)**
   - **Original**: Only a minimum length of 12 characters was enforced.
   - **Improved**: Implemented ASVS requirements to ensure stronger passwords and added a password strength meter.

2. **Multi-Factor Authentication (MFA) (V2.8.1)**
   - **Original**: No MFA was implemented.
   - **Improved**: Introduced MFA using Time-based One-Time Password (TOTP) with Google Authenticator.

3. **Password Security (V2.1.7)**
   - **Original**: No check for breached passwords.
   - **Improved**: Integrated a verification mechanism against a database of breached passwords using the "Have I Been Pwned?" API.

4. **Input Validation Requirements (V5.1.4)**
   - **Original**: Inadequate validation for user reviews.
   - **Improved**: Limited review length to 300 characters and restricted allowable characters.

5. **Session Expiration (V3.7.1)**
   - **Original**: Sessions were not properly validated for sensitive actions.
   - **Improved**: Implemented mandatory session validation and re-authentication for sensitive operations.

6. **File Upload (V12.1.1)**
   - **Original**: No checks on file upload sizes.
   - **Improved**: Set a maximum file size to prevent malware injection and data exposure.

7. **Cookie-based Session Management (V3.4.1)**
   - **Original**: Cookies were transmitted insecurely.
   - **Improved**: Ensured that session cookies are only transmitted over HTTPS.

8. **File Download Requirements (V12.5.1)**
   - **Original**: No restrictions on file types available for download.
   - **Improved**: Implemented checks to serve only specific file types, preventing access to sensitive files.

9. **Sensitive Private Data (V8.3.2)**
   - **Original**: Users could not delete or export their data.
   - **Improved**: Added functionality to allow users to delete or export their personal data on request.

10. **Session Binding (V3.2.2)**
    - **Original**: Session tokens lacked sufficient entropy.
    - **Improved**: Enhanced token generation to ensure at least 64 bits of entropy for better session security.
