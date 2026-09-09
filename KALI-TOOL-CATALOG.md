> **Reference file, not a requirement.** This is a lookup table, not a specification — it
> defines nothing, mandates nothing, and doesn't need `CLAUDE.md` §5's schema. It exists
> so the Strategist/Primary Scripter/Secondary Scripter can look up candidate tool
> *names* for a task domain that has no dedicated Tier 1 schema yet (per
> `01:FR-DISCOVER-01`, staged in `STAGING-Pending-Discussions-and-Fixes.md`). Build/
> Requirements-authoring agents should treat this the same way they'd treat a man page —
> data to consult when relevant, not something that defines system behavior on its own.
>
> Pulled directly from this machine's own `apt-cache show` output against Kali Rolling
> 2026.3 (`kali-linux-everything` and each of its category metapackages) — this is the
> real, current, authoritative tool set actually available/installable here, not a
> hand-typed approximation. Re-run the same `apt-cache show <package>` commands to
> refresh this file after a Kali release bump; tool sets do shift between releases.

---

## How to use this file

1. Have a task that doesn't fit an existing named Tier 1 tool? Find the closest category
   below by purpose (wireless, passwords, forensics, etc.).
2. Check candidate names against what's actually installed (`shutil.which`, per
   `01:FR-DISCOVER-02`) before treating any of them as callable.
3. Anything found here is reachable via the existing Tier 2 dynamic bridge
   (`01:FR-TOOL-03`) without needing a new Tier 1 schema — this file makes tools
   *discoverable*, it doesn't gate what's callable.
4. Not finding what you need here? This list is `kali-linux-everything`'s dependency
   tree, not literally every package in the Kali archive — a tool genuinely absent from
   both this file and `apt-cache search <keyword>` probably doesn't exist as a packaged
   Kali tool.

---

## By Category (Kali's own official tool-category metapackages)

### Wireless — 802.11 / WiFi (`kali-tools-802-11`)
`aircrack-ng` (the classic WEP/WPA suite: monitor mode, capture, deauth, cracking) ·
`airgeddon` (all-in-one wireless auditing menu wrapping several of these) · `asleap` ·
`bully` (WPS brute-force, alternative to `reaver`) · `cowpatty` · `eapmd5pass` ·
`fern-wifi-cracker` (GUI wrapper) · `freeradius-wpe` · `hashcat` (GPU cracking, also in
Passwords) · `hostapd-wpe` · `iw` (modern wireless config, replaces `iwconfig`) ·
`kismet` (passive wireless IDS/sniffer) · `macchanger` · `mdk3`/`mdk4` (wireless DoS/
testing frame injection) · `pixiewps` (WPS pixie-dust attack) · `reaver` (WPS
brute-force) · `wifi-honey` (rogue AP honeypot) · `wifite` (automated aircrack-ng
wrapper)

### Wireless — Bluetooth (`kali-tools-bluetooth`)
`blue-hydra` (BLE/BR device discovery daemon) · `bluelog` (Bluetooth site survey/
logging) · `blueranger` (proximity/RSSI-based device locator) · `bluesnarfer` ·
`bluez` (the Linux Bluetooth stack itself — `bluetoothctl`/`hcitool`/`gatttool` all
ship with this) · `btscanner` · `crackle` (BLE encryption cracking) · `redfang`
(discover non-discoverable devices) · `spooftooph` (BT identity spoofing) · `ubertooth`
(Ubertooth One hardware sniffer tools)

### Wireless — RFID (`kali-tools-rfid`)
`gnuradio` (also SDR) · `proxmark3` (the RFID/NFC research tool) · `rfdump`

### Wireless — SDR (`kali-tools-sdr`)
`chirp` · `gnuradio` · `gqrx-sdr` · `gr-air-modes` · `gr-iqbal` · `gr-osmosdr` ·
`hackrf` · `inspectrum` · `kalibrate-rtl` · `multimon-ng` · `uhd-host`/`uhd-images`
(USRP support)

### Information Gathering (`kali-tools-information-gathering`)
`0trace` · `arping` · `braa` · `dmitry` · `dnsenum` · `dnsmap` · `dnsrecon` ·
`dnstracer` · `dnswalk` · `enum4linux` · `fierce` · `firewalk` · `fping` ·
`fragrouter` · `ftester` · `hping3` · `ike-scan` · `intrace` · `irpas` · `lbd` ·
`legion` · `maltego` · `masscan` · `metagoofil` · `nbtscan` · `ncat` · `netdiscover` ·
`netmask` · `nmap` · `onesixtyone` · `p0f` · `qsslcaudit` · `recon-ng` · `smbmap` ·
`smtp-user-enum` · `snmpcheck` · `ssldump` · `sslh` · `sslscan` · `sslyze` · `swaks` ·
`thc-ipv6` · `theharvester` · `tlssled` · `twofi` · `unicornscan` · `urlcrazy` ·
`wafw00f` (already Tier 1) · `zenmap`

### Vulnerability Scanning (`kali-tools-vulnerability`)
`afl++` (also Fuzzing) · `bed` · `cisco-auditing-tool` · `cisco-global-exploiter` ·
`cisco-ocs` · `cisco-torch` · `copy-router-config` · `dhcpig` · `enumiax` · `gvm`
(OpenVAS/Greenbone) · `iaxflood` · `inviteflood` · `legion` · `lynis` · `nikto`
(already Tier 1) · `nmap` · `ohrwurm` · `peass` · `protos-sip` · `rtpbreak`/
`rtpflood`/`rtpinsertsound`/`rtpmixsound` · `sctpscan` · `sfuzz` · `siege` ·
`siparmyknife` · `sipp` · `sipsak` · `sipvicious` · `slowhttptest` · `spike` · `t50` ·
`thc-ssl-dos` · `unix-privesc-check` · `voiphopper` · `yersinia`

### Web Applications (`kali-tools-web`)
`apache-users` · `apache2` · `beef-xss` · `burpsuite` · `cadaver` · `commix` ·
`cutycapt` · `davtest` · `dirb` · `dirbuster` · `dotdotpwn` · `eyewitness` (already in
`FR-BASELINE`) · `ferret-sidejack` · `ftester` · `hakrawler` (already in
`FR-BASELINE`) · `hamster-sidejack` · `heartleech` · `httprint` · `httrack` · `hydra`/
`hydra-gtk` · `jboss-autopwn` · `joomscan` · `jsql-injection` · `laudanum` · `lbd` ·
`maltego` · `medusa` · `mitmproxy` · `ncrack` · `nikto` · `nishang` · `oscanner` ·
`owasp-mantra-ff` · `padbuster` · `paros` · `patator` · `proxychains4` · `proxytunnel` ·
`qsslcaudit` · `redsocks` · `sidguesser` · `siege` · `skipfish` · `slowhttptest` ·
`sqldict` · `sqlitebrowser` · `sqlmap` (already Tier 1) · `sqlninja` · `sqlsus` ·
`ssldump` · `sslh` · `sslscan` · `sslsniff` · `sslsplit` · `sslyze` · `stunnel4` ·
`thc-ssl-dos` · `tlssled` · `tnscmd10g` · `uniscan` · `wafw00f` · `wapiti` · `watobo` ·
`webacoo` · `webscarab` · `webshells` · `weevely` · `wfuzz` (also Fuzzing) ·
`whatweb` (already Tier 1) · `wireshark` · `wpscan` · `xsser` · `zaproxy` (OWASP ZAP)

### Database Assessment (`kali-tools-database`)
`jsql-injection` · `mdbtools` · `oscanner` · `sidguesser` · `sqldict` ·
`sqlitebrowser` · `sqlmap` · `sqlninja` · `sqlsus` · `tnscmd10g`

### Password Attacks (`kali-tools-passwords`)
`cewl` · `chntpw` · `cisco-auditing-tool` · `cmospwd` · `crackle` · `creddump7` ·
`crunch` · `fcrackzip` · `freerdp3-x11` · `gpp-decrypt` · `hash-identifier` ·
`hashcat`/`hashcat-utils` · `hashid` · `hydra`/`hydra-gtk` · `john`/`johnny` (John the
Ripper) · `maskprocessor` · `medusa` · `mimikatz` · `ncrack` · `onesixtyone` ·
`ophcrack`/`ophcrack-cli` · `pack`/`pack2` · `passing-the-hash` · `patator` ·
`pdfcrack` · `pipal` · `polenum` · `rainbowcrack` · `rarcrack` · `rcracki-mt` ·
`rsmangler` · `samdump2` · `seclists` (wordlists) · `sipcrack` · `sipvicious` ·
`smbmap` · `sqldict` · `statsprocessor` · `sucrack` · `thc-pptp-bruter` · `truecrack` ·
`twofi` · `wordlists`

### Reverse Engineering (`kali-tools-reverse-engineering`)
`apktool` · `bytecode-viewer` · `clang` · `dex2jar` · `edb-debugger` · `jadx`
(already in `FR-BASELINE`) · `javasnoop` · `jd-gui` · `metasploit-framework` ·
`ollydbg` · `radare2` · `rizin`/`rizin-cutter` · `rz-ghidra`

### Exploitation Tools (`kali-tools-exploitation`)
`armitage` · `beef-xss` · `exploitdb` · `metasploit-framework` · `msfpc` · `set`
(Social-Engineer Toolkit) · `shellnoob` · `sqlmap` · `termineter`

### Social Engineering (`kali-tools-social-engineering`)
`beef-xss` · `maltego` · `msfpc` · `set` · `veil`

### Sniffing & Spoofing (`kali-tools-sniffing-spoofing`)
`bettercap` · `darkstat` · `dnschef` · `driftnet` · `dsniff` · `ettercap-graphical`/
`ettercap-text-only` · `ferret-sidejack` · `fiked` · `hamster-sidejack` ·
`hexinject` · `isr-evilgrade` · `macchanger` · `mitmproxy` · `netsniff-ng` ·
`rebind` · `responder` · `sniffjoke` · `sslsniff` · `sslsplit` · `tcpflow` ·
`tcpreplay` · `wifi-honey` · `wireshark`

### Post Exploitation (`kali-tools-post-exploitation`)
`cymothoa` · `dbd` · `dns2tcp` · `exe2hexbat` · `iodine` · `laudanum` · `mimikatz` ·
`miredo` · `nishang` · `powersploit` · `proxychains4` · `proxytunnel` · `ptunnel` ·
`pwnat` · `sbd` · `shellter` · `sslh` · `stunnel4` · `udptunnel` · `veil` ·
`webacoo` · `weevely`

### Forensics (`kali-tools-forensics`)
`7zip` · `afflib-tools` · `apktool` · `autopsy` · `binwalk`/`binwalk3` ·
`bulk-extractor` · `cabextract` · `chkrootkit` · `creddump7` · `dc3dd` · `dcfldd` ·
`ddrescue` · `ewf-tools` · `exifprobe` · `exiv2` · `ext3grep`/`ext4magic`/
`extundelete` · `fcrackzip` · `firmware-mod-kit` · `foremost` · `forensic-artifacts` ·
`galleta` · `gdb` · `gpart`/`gparted` · `grokevt` · `guymager` · `hashdeep` ·
`inetsim` · `jadx` · `javasnoop` · `libhivex-bin` · `libsmali-java` · `lvm2` ·
`lynis` · `mac-robber` · `magicrescue` · `md5deep` · `mdbtools` · `memdump` ·
`metacam` · `missidentify` · `myrescue` · `nasm` · `ollydbg` · `parted` · `pasco` ·
`pdf-parser`/`pdfid` · `plaso` · `polenum` · `pst-utils` · `radare2` · `readpe` ·
`recoverdm`/`recoverjpeg` · `reglookup` · `regripper` · `rifiuti`/`rifiuti2` ·
`rizin-cutter` · `rkhunter` · `rsakeyfind` · `rz-ghidra` · `safecopy` · `samdump2` ·
`scalpel` · `scrounge-ntfs` · `sleuthkit` · `sqlitebrowser` · `ssdeep` · `tcpdump` ·
`tcpflow`/`tcpick`/`tcpreplay` · `truecrack` · `undbx` · `unhide` · `unrar`/`unar` ·
`upx-ucl` · `vinetto` · `wce` · `winregfs` · `wireshark` · `xmount` · `xplico` ·
`yara`

### Reporting Tools (`kali-tools-reporting`)
`cutycapt` · `dradis` · `eyewitness` · `faraday` · `maltego` · `metagoofil` ·
`pipal` · `recordmydesktop`

### Identify / Protect / Detect / Respond / Recover (NIST-CSF-mapped categories)
- **Identify** (`kali-tools-identify`): `amass` (already registered) · `assetfinder`
  (already registered) · `cisco-auditing-tool` · `defectdojo` · `exploitdb` ·
  `hb-honeypot` · `kali-autopilot` · `maltego` · `maryam` · `nipper-ng` ·
  `osrframework` · `spiderfoot` · `tiger` · `wapiti` · `witnessme` · `zaproxy`
- **Protect** (`kali-tools-protect`): `clamav` · `cryptsetup` (+`-initramfs`/
  `-nuke-password`) · `fwbuilder`
- **Detect** (`kali-tools-detect`): `grokevt` · `sentrypeer`
- **Respond** (`kali-tools-respond`): everything in Forensics, plus `ghidra` ·
  `hashrat` · `impacket-scripts` · `netsniff-ng`
- **Recover** (`kali-tools-recover`): `ddrescue` · `ext3grep` · `extundelete` ·
  `myrescue` · `recoverdm` · `recoverjpeg` · `scrounge-ntfs` · `undbx`

### Crypto & Stego (`kali-tools-crypto-stego`)
`aesfix`/`aeskeyfind` · `ccrypt` · `steghide` · `stegosuite` · `stegsnow`

### Fuzzing (`kali-tools-fuzzing`)
`afl++` · `sfuzz` · `spike` · `wfuzz`

### GPU-Accelerated Cracking (`kali-tools-gpu`)
`oclgausscrack` · `truecrack`

### Hardware Hacking (`kali-tools-hardware`)
`binwalk`/`binwalk3` · `cutecom` · `flashrom` · `minicom` · `openocd` ·
`qemu-system-x86`/`qemu-user` · `radare2` · `rizin-cutter` · `rz-ghidra`

### VoIP (`kali-tools-voip`)
`enumiax` · `iaxflood` · `inviteflood` · `libfindrtp` · `nmap` · `ohrwurm` ·
`protos-sip` · `rtpbreak`/`rtpflood`/`rtpinsertsound`/`rtpmixsound` · `sctpscan` ·
`siparmyknife` · `sipcrack` · `sipp` · `sipvicious` · `voiphopper` · `wireshark`

### Windows Resources (`kali-tools-windows-resources`)
`dbd` · `dnschef` · `heartleech` · `hyperion` · `mimikatz` · `ncat-w32` · `ollydbg` ·
`powercat` · `regripper` · `sbd` · `secure-socket-funneling-windows-binaries` ·
`shellter` · `tftpd32` · `wce` · `windows-binaries` · `windows-privesc-config`

### Top 10 (`kali-tools-top10` — Kali's own "if you only had 10" shortlist)
`aircrack-ng` · `burpsuite` · `hydra` · `john` · `metasploit-framework` · `netexec` ·
`nmap` · `responder` · `sqlmap` · `wireshark`

---

## Additional Tools Bundled Directly (not under a dedicated category metapackage above)

These ship as direct dependencies of `kali-linux-everything` itself, not through one of
the category metapackages — a mix of Active Directory/Windows-domain tooling, OSINT,
C2 frameworks, cloud tooling, and newer additions not yet folded into a category above.
Grouped loosely by apparent purpose (not an official Kali grouping, just for
scannability):

**Active Directory / Windows domain**: `bloodhound`, `bloodhound.py`,
`bloodhound-ce-python`, `bloodyad`, `crackmapexec`, `netexec` (successor to
crackmapexec), `coercer`, `certgraph`, `certi`, `evil-winrm-py`, `impacket`-family
(via `impacket-scripts` above), `kerberoast`, `krbrelayx`, `ldeep`, `lapsdumper`,
`mitm6`, `mssqlpwner`, `peirates`, `rubeus`, `sharphound`, `snaffler-ng`, `sprayhound`,
`spraykatz`

**C2 / post-exploitation frameworks**: `adaptixc2`, `havoc`, `merlin-agent`/
`merlin-server`, `poshc2`, `silenttrinity`, `sliver`, `villain`

**Cloud (AWS/Azure/GCP/Kubernetes)**: `azurehound`, `calicoctl`, `cilium-cli`,
`cri-tools`, `eksctl`, `kubernetes-helm`, `kustomize`, `pacu`, `terraform`

**Credential spraying / brute-force**: `brutespray`, `changeme`, `crowbar`, `legba`,
`multiforcer`, `spray`, `sprayingtoolkit`

**OSINT / recon**: `altdns`, `dnsgen`, `dnstwist`, `email2phonenumber`,
`emailharvester`, `findomain`, `getallurls`, `gitxray`, `goofile`, `h8mail`,
`hosthunter`, `inspy`, `instaloader`, `ismtp`, `ivre`, `linkedin2username`, `photon`,
`reconspider`, `sherlock`, `sn0int`, `tookie-osint`, `waybackpy`

**Web/API scanning & exploitation extras**: `arjun` (already registered), `caido`/
`caido-cli`, `cmseek`, `dirsearch`, `crlfuzz`, `finalrecon`, `httpx-toolkit`,
`humble`, `katana` (already registered), `naabu` (already registered), `nuclei`
(already registered), `s3scanner` (already registered), `subfinder` (already
registered), `subjack` (already registered), `trufflehog` (already registered),
`web-cache-vulnerability-scanner`, `wpprobe`, `xsrfprobe`, `xsstrike`, `gospider`
(already registered), `robotstxt`, `uro`, `wgetpaste`

**Exploit development / binary**: `donut`, `getsploit`, `golang-github-binject-go-donut`,
`gdb-peda`, `gef`, `linux-exploit-suggester`, `patchleaks`, `pwncat`, `quark-engine`,
`ropper`, `routersploit`, `sploitscan`, `stegcracker`

**Networking / tunneling / pivoting**: `chisel`, `chisel-common-binaries`, `dnscat2`,
`ligolo-mp`/`ligolo-ng`/`ligolo-ng-common-binaries`, `proxify`, `pspy`, `rev-proxy-grapher`,
`sshuttle`, `sslstrip`, `tailscale`, `vopono`

**Wireless (bundled directly, beyond the 802-11/Bluetooth category lists above)**:
`berate-ap`, `eaphammer`, `fluxion`, `hak5-wifi-coconut`, `horst`, `sparrow-wifi`,
`vwifi-tool`, `wifiphisher`, `wifipumpkin3`, `wig`/`wig-ng`, `wpa-sycophant`

**Phishing / social engineering extras**: `evilginx2`, `evil-ssdp`, `wifiphisher`,
`gophish`-adjacent tooling not listed separately here

**Reporting / vuln management platforms**: `defectdojo` (also under Identify),
`faraday-agent-dispatcher`/`faraday-cli`, `redeye`

**Misc security utilities**: `apple-bleee`, `arsenal-ng`, `autorecon`, `b374k`,
`bing-ip2hosts`, `bopscrk`, `bpf-linker`, `bruteforce-luks`/`bruteforce-salted-openssl`/
`bruteforce-wallet`, `bruteshark`, `capstone-tool`, `chainsaw`, `cisco7crack`,
`cloud-enum` (already registered), `cloudbrute`, `cntlm`, `cosign`, `crack`,
`cupid-hostapd`/`cupid-wpasupplicant`, `detect-it-easy`, `dislocker`, `dscan`,
`dufflebag`, `dumpsterdiver`, `dwarf2json`, `enum4linux-ng`, `exiflooter`,
`fatcat`, `gitleaks` (already registered), `godoh`, `goldeneye`, `goshs`, `gowitness`,
`graudit`, `gsocket`, `gtkhash`, `hb-honeypot`, `hcxtools`, `hekatomb`, `hexstrike-ai`,
`hexwalk`, `hoaxshell`, `hostsman`, `htshells`, `hubble`, `hurl`, `ibombshell`,
`ident-user-enum`, `imhex`, `jsp-file-browser`, `knocker`, `koadic`, `maltego-teeth`,
`mcp-kali-server`, `metasploitmcp`, `mongo-tools`, `mxcheck`, `name-that-hash`,
`nbtscan-unixwiz`, `netscanner`, `nextnet`, `nmapsi4`, `obsidian`, `odat`, `oletools`,
`opentaxii`, `owl`, `parsero`, `passdetective`, `payloadsallthethings`, `phishery`,
`phpggc`, `phpsploit`, `pnscan`, `pocsuite3`, `pompem`, `portspoof`, `princeprocessor`,
`proximoth`, `proxmark3` (also RFID), `pskracker`, `pyinstxtractor`,
`python3-atomic-operator`, `python3-ciphey`, `python3-dploot`, `python3-ldapdomaindump`,
`python3-pyinstaller`, `python3-wsgidav`, `raven`, `ridenum`, `rling`, `routerkeygenpc`,
`ruby-pedump`, `sara`, `sentrypeer`, `sharpshooter`, `shed`, `shellfire`, `shell-gpt`,
`sickle-pdk`, `sigma-cli`, `sippts`, `slimtoolkit`, `snmpenum`, `snort`, `snowdrop`,
`sqlmc`, `sstimap`, `syft`, `teamsploit`, `tetragon`, `tinja`, `trivy`, `tundeep`,
`unblob`, `unicorn-magic`, `websploit`, `whatmask`, `witnessme`, `wixl`, `wmi-client`,
`wordlistraider`, `wotmate`, `xclip`, `zonedb`

---

*(This file is a Kali package/tool census, not a project decision log — additions here
don't need `CLAUDE.md` §5's schema or a decision-log entry the way an actual requirement
change does. Re-running the `apt-cache show` commands after a Kali point release is
enough to keep it current.)*
