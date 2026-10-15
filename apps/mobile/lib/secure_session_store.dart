import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Only native HTTPS sessions use this store. Web authentication stays in the
/// server's HttpOnly cookie; passwords never enter this store.
String? nativeSessionScope(String backend) {
  final uri = Uri.tryParse(backend.trim());
  if (uri == null ||
      uri.scheme != 'https' ||
      uri.host.isEmpty ||
      uri.userInfo.isNotEmpty ||
      uri.hasQuery ||
      uri.hasFragment) {
    return null;
  }
  final path = uri.normalizePath().path.replaceFirst(RegExp(r'/+$'), '');
  return Uri(
    scheme: 'https',
    host: uri.host.toLowerCase(),
    port: uri.port == 443 ? null : uri.port,
    path: path,
  ).toString();
}

class NativeSession {
  const NativeSession({required this.token, required this.accountId});
  final String token;
  final String accountId;
}

class SecureSessionStorageException implements Exception {
  const SecureSessionStorageException();
  @override
  String toString() =>
      'Chưa truy cập được nơi lưu phiên đăng nhập an toàn. Hãy mở khóa thiết bị rồi thử lại.';
}

abstract interface class SessionSecretStorage {
  Future<String?> read(String key);
  Future<void> write(String key, String value);
  Future<void> delete(String key);
}

class PlatformSessionSecretStorage implements SessionSecretStorage {
  const PlatformSessionSecretStorage();

  // Explicit authenticated encryption avoids the plugin's legacy default
  // ciphers. API 24 is our minimum; OAEP/GCM are available from API 23.
  static const platform = FlutterSecureStorage(
    aOptions: AndroidOptions(
      sharedPreferencesName: 'tu_hoc_111_native_sessions',
      preferencesKeyPrefix: 'tu_hoc_111_sessions_v1_',
      resetOnError: false,
      keyCipherAlgorithm:
          KeyCipherAlgorithm.RSA_ECB_OAEPwithSHA_256andMGF1Padding,
      storageCipherAlgorithm: StorageCipherAlgorithm.AES_GCM_NoPadding,
    ),
    iOptions: IOSOptions(
      accountName: 'vn.khohoc.native_sessions.v1',
      accessibility: KeychainAccessibility.unlocked_this_device,
      synchronizable: false,
    ),
  );

  @override
  Future<String?> read(String key) => platform.read(key: key);
  @override
  Future<void> write(String key, String value) =>
      platform.write(key: key, value: value);
  @override
  Future<void> delete(String key) => platform.delete(key: key);
}

class SecureSessionStore {
  SecureSessionStore(this.storage);
  final SessionSecretStorage storage;
  Future<void> _tail = Future<void>.value();

  Future<T> _serialized<T>(Future<T> Function() action) {
    final work = _tail.then((_) async {
      try {
        return await action();
      } catch (_) {
        // A platform exception can contain native details. Never expose it or
        // its arguments (which can include a bearer token) to the UI or logs.
        throw const SecureSessionStorageException();
      }
    });
    _tail = work.then<void>((_) {}, onError: (Object _, StackTrace __) {});
    return work;
  }

  String _key(String scope) {
    if (nativeSessionScope(scope) != scope) {
      throw ArgumentError('Session scope must be a normalized HTTPS backend');
    }
    return 'session_v1.${base64UrlEncode(utf8.encode(scope)).replaceAll('=', '')}';
  }

  NativeSession? _decode(String? value) {
    if (value == null) return null;
    try {
      final record = jsonDecode(value);
      if (record is! Map ||
          record['schema'] != 1 ||
          record['token'] is! String ||
          !RegExp(r'^khs_[A-Za-z0-9_-]{20,128}$').hasMatch(record['token']) ||
          record['account_id'] is! String ||
          record['account_id'].isEmpty ||
          record['account_id'].length > 128) {
        return null;
      }
      return NativeSession(
        token: record['token'],
        accountId: record['account_id'],
      );
    } catch (_) {
      return null;
    }
  }

  Future<NativeSession?> read(String scope) => _serialized(() async {
    final key = _key(scope);
    final value = await storage.read(key);
    final record = _decode(value);
    if (value != null && record == null) await storage.delete(key);
    return record;
  });

  Future<bool> write(
    String scope,
    NativeSession session, {
    bool Function()? isCurrent,
  }) => _serialized(() async {
    final key = _key(scope);
    final value = jsonEncode({
      'schema': 1,
      'token': session.token,
      'account_id': session.accountId,
    });
    if (_decode(value) == null) {
      throw ArgumentError('Invalid native session');
    }
    if (isCurrent != null && !isCurrent()) return false;
    await storage.write(key, value);
    return true;
  });

  /// A delayed 401/logout from an old client must not erase a newer login.
  Future<bool> clearIfToken(String scope, String token) =>
      _serialized(() async {
        final key = _key(scope);
        final current = _decode(await storage.read(key));
        if (current?.token != token) return false;
        await storage.delete(key);
        return true;
      });
}

final _nativeStore = SecureSessionStore(const PlatformSessionSecretStorage());

SecureSessionStore? nativeSecureSessionStore() {
  if (kIsWeb ||
      ![
        TargetPlatform.android,
        TargetPlatform.iOS,
      ].contains(defaultTargetPlatform)) {
    return null;
  }
  return _nativeStore;
}
