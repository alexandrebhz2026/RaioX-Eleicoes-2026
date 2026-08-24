# Google login experiment

The Google login path is intentionally isolated from application startup. The native Google module is loaded only after an explicit user action. Firebase authentication continues to use REST; Firebase JS is not used.
