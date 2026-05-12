import 'dart:convert';
import 'dart:math';
import 'package:http/http.dart' as http;
import 'package:crypto/crypto.dart';

class GabopayException implements Exception {
  final String message;
  final int? statusCode;
  final String? code;

  GabopayException(this.message, {this.statusCode, this.code});

  @override
  String toString() => 'GabopayException: $message';
}

class Gabopay {
  final String secretKey;
  final String baseUrl;
  final Duration timeout;

  Gabopay({
    required this.secretKey,
    this.baseUrl = 'https://api.gabopay.ga',
    this.timeout = const Duration(seconds: 60),
  });

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'X-API-Key': secretKey,
      };

  Future<Map<String, dynamic>> _request(
    String method,
    String path, {
    Map<String, dynamic>? body,
  }) async {
    final uri = Uri.parse('$baseUrl$path');
    final request = http.Request(method, uri);
    request.headers.addAll(_headers);

    if (body != null) {
      request.body = jsonEncode(body);
    }

    final response = await request.send().timeout(timeout);

    if (response.statusCode >= 400) {
      final errorBody = jsonDecode(await response.stream.bytesToString());
      throw GabopayException(
        errorBody['error']?['message'] ?? 'Request failed',
        statusCode: response.statusCode,
        code: errorBody['error']?['code'],
      );
    }

    return jsonDecode(await response.stream.bytesToString());
  }

  /// Create a payment charge
  Future<Map<String, dynamic>> createCharge({
    required int amount,
    String currency = 'XAF',
    required String method,
    String? phone,
    String? description,
    Map<String, dynamic>? metadata,
  }) async {
    return _request('POST', '/v1/charges', body: {
      'amount': amount,
      'currency': currency,
      'method': method,
      if (phone != null) 'phone': phone,
      if (description != null) 'description': description,
      if (metadata != null) 'metadata': metadata,
    });
  }

  /// Get a charge by ID
  Future<Map<String, dynamic>> getCharge(String chargeId) async {
    return _request('GET', '/v1/charges/$chargeId');
  }

  /// List charges
  Future<Map<String, dynamic>> listCharges({int limit = 20, String? status}) async {
    final queryParams = {'limit': limit.toString()};
    if (status != null) queryParams['status'] = status;
    final query = Uri(queryParameters: queryParams).query;
    return _request('GET', '/v1/charges?$query');
  }

  /// Create a refund
  Future<Map<String, dynamic>> createRefund(
    String transactionId, {
    required int amount,
    String? reason,
  }) async {
    return _request('POST', '/v1/refunds/$transactionId', body: {
      'amount': amount,
      if (reason != null) 'reason': reason,
    });
  }

  /// Create a payout
  Future<Map<String, dynamic>> createPayout({
    required int amount,
    required String method,
    required String phone,
  }) async {
    return _request('POST', '/v1/payouts', body: {
      'amount': amount,
      'method': method,
      'phone': phone,
    });
  }

  /// Get merchant balance
  Future<Map<String, dynamic>> getBalance() async {
    return _request('GET', '/v1/balance');
  }

  /// Constant-time string comparison to prevent timing attacks
  static bool _constantTimeEquals(String a, String b) {
    if (a.length != b.length) {
      var result = a.length ^ b.length;
      final minLen = a.length < b.length ? a.length : b.length;
      for (var i = 0; i < minLen; i++) {
        result |= a.codeUnitAt(i) ^ b.codeUnitAt(i);
      }
      return result == 0;
    }
    var result = 0;
    for (var i = 0; i < a.length; i++) {
      result |= a.codeUnitAt(i) ^ b.codeUnitAt(i);
    }
    return result == 0;
  }

  /// Verify webhook signature
  static bool verifyWebhookSignature(
    String payload,
    String signature,
    String secret,
  ) {
    if (signature.isEmpty) {
      throw GabopayException('Signature is required');
    }
    if (secret.isEmpty) {
      throw GabopayException('Secret is required');
    }

    try {
      final parts = signature.split(',');
      final params = <String, String>{};
      for (final part in parts) {
        final kv = part.split('=');
        if (kv.length == 2) {
          params[kv[0]] = kv[1];
        }
      }

      final timestamp = int.tryParse(params['t'] ?? '');
      if (timestamp == null) return false;

      final now = DateTime.now().millisecondsSinceEpoch ~/ 1000;
      if ((now - timestamp).abs() > 300) return false;

      final expectedSig = params['v1'];
      if (expectedSig == null || expectedSig.isEmpty) return false;

      final signedPayload = '$timestamp.$payload';
      final computed = Hmac(sha256, secret.encode())
          .convert(signedPayload.encode())
          .toString();

      return _constantTimeEquals(computed, expectedSig);
    } catch (_) {
      return false;
    }
  }

  /// Construct webhook event
  static Map<String, dynamic> constructWebhookEvent(
    String payload,
    String signature,
    String secret,
  ) {
    if (signature.isEmpty) {
      throw GabopayException('Signature is required');
    }
    if (secret.isEmpty) {
      throw GabopayException('Secret is required');
    }
    if (!verifyWebhookSignature(payload, signature, secret)) {
      throw GabopayException('Invalid webhook signature');
    }
    return jsonDecode(payload);
  }
}
