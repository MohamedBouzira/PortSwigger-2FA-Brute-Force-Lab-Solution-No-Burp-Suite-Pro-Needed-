# PortSwigger-2FA-Brute-Force-Lab-Solution-(No-Burp-Suite-Pro-Needed)
Python tool to solve the PortSwigger lab without Burp Suite Pro. Automates login, handles brute-force protection, and saves hours for hackers stuck with Burp Community.

**Lab:** 2FA bypass using a brute-force attack  
**Difficulty:** Expert  

## 💡 Idea
The lab has brute-force protection: after **2 wrong attempts**, you get logged out.  
This means you need a **macro** to re-authenticate for each guess.  
Burp Pro does this easily — but with Burp Community ,the Intruder is extremely slow and session handling is limited.

## ✅ Solution
This Python tool automates the entire process:
- Logs in.
- Tries a 2FA code.
- Re-authenticates automatically after logout.
- Works much faster than Burp Community.

## 📌 Note
In a **real-world scenario**, the chance of guessing correctly is **1/10000**  
because the 2FA code regenerates after each try.  
However, in this PortSwigger lab, it’s designed to be solvable.

## 🛠 Tools
- `bruteforce_2fa.py` — Basic single-threaded version.
- `bruteforce_2fa_optimized.py` — Faster, threaded, fully automatic version.

## 🚀 Usage
1. **Clone the repo**  
   ```bash
   git clone <repo.git>
   cd 2fa-bypass-lab
   ```
2. **generate a 4-digit code list**  
   ```bash
   seq -w 0000 9999 > list.txt
   ```
3. **edit the script**  
    edit url variable in the script
4. **Run the script**  
   ```bash
   python3 bruteforce_2fa_optimized.py
   ```
