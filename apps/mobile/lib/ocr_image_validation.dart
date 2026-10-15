import 'dart:typed_data';

/// Inspect dimensions before handing untrusted image bytes to a native decoder.
/// The decoder still validates the full image after these allocation limits.
class OcrImageSize {
  const OcrImageSize(this.width, this.height);
  final int width;
  final int height;
}

const maxOcrImageBytes = 8 * 1024 * 1024;

OcrImageSize validateOcrImage(Uint8List bytes) {
  if (bytes.isEmpty || bytes.length > maxOcrImageBytes) {
    throw const FormatException('Chọn ảnh có dung lượng từ 1 byte đến 8 MiB.');
  }
  final data = ByteData.sublistView(bytes);
  bool ascii(int start, String text) =>
      start + text.length <= bytes.length &&
      text.codeUnits.asMap().entries.every(
        (e) => bytes[start + e.key] == e.value,
      );
  OcrImageSize checked(int width, int height) {
    if (width < 1 ||
        height < 1 ||
        width > 6000 ||
        height > 6000 ||
        width * height > 16000000) {
      throw const FormatException(
        'Ảnh quá lớn hoặc không hợp lệ. Chọn ảnh tối đa 16 triệu điểm ảnh, mỗi chiều không quá 6.000 điểm ảnh.',
      );
    }
    return OcrImageSize(width, height);
  }

  if (bytes.length >= 45 &&
      bytes[0] == 137 &&
      ascii(1, 'PNG\r\n\u001a\n') &&
      data.getUint32(8) == 13 &&
      ascii(12, 'IHDR')) {
    // Reject animation, oversized or truncated chunks before decoding frames.
    var offset = 8;
    var ended = false;
    while (offset + 12 <= bytes.length) {
      final length = data.getUint32(offset);
      if (length > bytes.length - offset - 12) break;
      if (ascii(offset + 4, 'acTL')) {
        throw const FormatException('Chưa hỗ trợ ảnh động. Hãy chọn ảnh tĩnh.');
      }
      if (ascii(offset + 4, 'IEND')) {
        ended = length == 0;
        break;
      }
      offset += length + 12;
    }
    if (ended) return checked(data.getUint32(16), data.getUint32(20));
  }
  if (bytes.length >= 12 && bytes[0] == 255 && bytes[1] == 216) {
    var offset = 2;
    while (offset + 4 <= bytes.length) {
      if (bytes[offset++] != 255) break;
      while (offset < bytes.length && bytes[offset] == 255) {
        offset++;
      }
      if (offset >= bytes.length) break;
      final marker = bytes[offset++];
      if (marker == 0xd9 || marker == 0xda) break;
      if (marker == 0x01 || marker >= 0xd0 && marker <= 0xd7) continue;
      if (offset + 2 > bytes.length) break;
      final length = data.getUint16(offset);
      if (length < 2 || length > bytes.length - offset) break;
      if (const {
        0xc0,
        0xc1,
        0xc2,
        0xc3,
        0xc5,
        0xc6,
        0xc7,
        0xc9,
        0xca,
        0xcb,
        0xcd,
        0xce,
        0xcf,
      }.contains(marker)) {
        if (length < 8) break;
        return checked(data.getUint16(offset + 5), data.getUint16(offset + 3));
      }
      offset += length;
    }
  }
  if (bytes.length >= 30 &&
      ascii(0, 'RIFF') &&
      ascii(8, 'WEBP') &&
      data.getUint32(4, Endian.little) + 8 == bytes.length) {
    final length = data.getUint32(16, Endian.little);
    if (length + 20 <= bytes.length) {
      if (ascii(12, 'VP8X') && length == 10) {
        if (bytes[20] & 2 != 0) {
          throw const FormatException(
            'Chưa hỗ trợ ảnh động. Hãy chọn ảnh tĩnh.',
          );
        }
        int u24(int p) => bytes[p] + (bytes[p + 1] << 8) + (bytes[p + 2] << 16);
        return checked(u24(24) + 1, u24(27) + 1);
      }
      if (ascii(12, 'VP8 ') &&
          length >= 10 &&
          bytes[23] == 0x9d &&
          bytes[24] == 1 &&
          bytes[25] == 0x2a) {
        return checked(
          data.getUint16(26, Endian.little) & 0x3fff,
          data.getUint16(28, Endian.little) & 0x3fff,
        );
      }
      if (ascii(12, 'VP8L') && length >= 5 && bytes[20] == 0x2f) {
        final bits = data.getUint32(21, Endian.little);
        return checked((bits & 0x3fff) + 1, ((bits >> 14) & 0x3fff) + 1);
      }
    }
  }
  throw const FormatException(
    'Tệp không phải ảnh PNG, JPEG hoặc WebP hợp lệ. Hãy đổi ảnh HEIC thành JPEG hoặc PNG; chưa hỗ trợ PDF, SVG và GIF.',
  );
}
