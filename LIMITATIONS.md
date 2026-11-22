# Limitations & Privacy Considerations

## Technical Limitations

### Audio Capture
1. **Speakerphone Required**: Android 10+ blocks third-party apps from recording the actual phone call audio stream. SwaraGuard must rely on capturing audio from the microphone when the phone is in speakerphone mode.

2. **Noise Interference**: Background noise and overlapping conversations may reduce analysis accuracy.

3. **Audio Quality**: Compressed voice calls (VoLTE, 3G) may distort audio features important for deepfake detection.

### Call Termination
1. **ANSWER_PHONE_CALLS Permission**: Only system apps or devices with device admin rights can permanently grant this permission. Users will need to manually grant it, and some OEMs may block it.

2. **Workaround Required**: For production, SwaraGuard should prompt users to:
   - Use "Call disconnect" overlay
   - Provide manual "End Call" button
   - Suggest disabling speakerphone after threat is detected

### Bank Integration
1. **Simulated-Only**: Third-party apps cannot directly freeze bank accounts. Our "Bank Freeze" is a simulation for demonstration purposes.

2. **User Action Required**: Users must manually:
   - Open their bank's UPI app
   - Lock their debit/credit card
   - Change their UPI PIN
   - Contact their bank

### AI Analysis Accuracy
1. **Gemini API Dependent**: Full scam detection relies on Google's Gemini API availability and quotas.

2. **No Local Models**: AASIST and RawNet2 models for offline deepfake detection require significant model files (100MB+) and custom integration.

3. **Language Support**: Primary support for Hindi, Telugu, and English. Other Indian languages may have reduced accuracy.

## Privacy & Consent Notes

### Data Policy (For Presentation)

1. **End-to-End Encryption**
   - Audio is transmitted via HTTPS to our backend
   - No audio is stored on our servers
   - Processing is ephemeral (5-10 minutes)

2. **User Consent**
   - Users must explicitly grant RECORD_AUDIO permission
   - Permission rationale is explained in-app
   - Users can opt-out at any time

3. **No PII Collection**
   - Only risk scores and anonymized logs are stored
   - No personal conversations are recorded or processed
   - No user identifiers are retained

4. **GDPR/India DPA Compliance**
   ```
   Data Controller: N/A (demo project)
   Data Processor: N/A
   Retention Period: Processing only, no storage
   Right to Access: N/A (no data collected)
   Right to Erasure: N/A (no data to delete)
   ```

5. **Storage Minimization**
   - Audio chunks are deleted immediately after analysis
   - No cache directory persistence
   - Encrypted preferences for user settings only

### Permission Requirements

| Permission | Reason | Can be Denied |
|------------|--------|---------------|
| RECORD_AUDIO | Capture call audio from speakerphone | App has reduced functionality |
| FOREGROUND_SERVICE | Run analysis in background | Service stops when app in background |
| READ_PHONE_STATE | Detect incoming calls | Manual start required |
| ANSWER_PHONE_CALLS | End scam calls | Manual end call required |
| POST_NOTIFICATIONS | Alert user of high risk | No risk alerts |
| INTERNET | Call external APIs | App cannot analyze calls |

### Battery Impact
- Continuous audio recording drains ~8-12% battery/hour
- Network requests add ~3-5% battery/hour
- Estimated 15% battery for 10-minute call + analysis

## Disclaimer (Required for App Store Submission)

```
DISCLAIMER: This app uses AI to detect potential scam calls. While we strive
for accuracy, no software is 100% accurate. Always use your judgment and
verify information independently. We do not guarantee detection of all scam
calls. Bank transaction freezes must be done through your bank's official
channels. By using this app, you acknowledge that we are not liable for any
financial losses resulting from call activities.
```

## Known Issues

1. **Android 13+ Notification Permission**: Must be granted separately
2. **Samsung/MIUI Battery Optimization**: May kill foreground service
3. **Network Connectivity**: Offline mode limited to local processing
4. **Multitasking**: Audio focus conflicts with other apps
5. **International Numbers**: Currently only optimized for Indian calls

## Production Considerations

1. **Backend**: Replace simulation with actual partner integrations
2. **Models**: Add on-device deepfake detection models
3. **UI**: Material 3 compliance updates
4. **Testing**: Add UI tests with mock responses
5. **Analytics**: Add anonymized usage analytics (opt-in)
6. **Localization**: Add regional language support
7. **Accessibility**: Add TalkBack and color contrast fixes