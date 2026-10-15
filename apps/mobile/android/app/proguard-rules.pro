# google_mlkit_text_recognition 0.15.0 compiles optional script branches against
# compileOnly dependencies. Its README says only Latin is bundled by default.
# The app always sends TextRecognitionScript.latin (script=0); it does not ship
# or call these four optional models. Suppress only the eight absent option
# classes reported by R8, retaining shrinking and all other missing-class errors.
# If another script is enabled, add its supported runtime dependency and remove
# the corresponding suppression instead of using these rules to hide it.
-dontwarn com.google.mlkit.vision.text.chinese.ChineseTextRecognizerOptions$Builder
-dontwarn com.google.mlkit.vision.text.chinese.ChineseTextRecognizerOptions
-dontwarn com.google.mlkit.vision.text.devanagari.DevanagariTextRecognizerOptions$Builder
-dontwarn com.google.mlkit.vision.text.devanagari.DevanagariTextRecognizerOptions
-dontwarn com.google.mlkit.vision.text.japanese.JapaneseTextRecognizerOptions$Builder
-dontwarn com.google.mlkit.vision.text.japanese.JapaneseTextRecognizerOptions
-dontwarn com.google.mlkit.vision.text.korean.KoreanTextRecognizerOptions$Builder
-dontwarn com.google.mlkit.vision.text.korean.KoreanTextRecognizerOptions
