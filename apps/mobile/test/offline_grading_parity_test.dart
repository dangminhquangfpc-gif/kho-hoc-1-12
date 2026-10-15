import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:kho_hoc_mobile/offline_grading.dart';

typedef Json = Map<String, dynamic>;

Json readFixture(String path) =>
    jsonDecode(File(path).readAsStringSync()) as Json;

void expectScore(dynamic actual, dynamic expected, String reason) {
  if (expected == null) {
    expect(actual, isNull, reason: reason);
  } else {
    expect(actual, isA<num>(), reason: reason);
    expect(
      (actual as num).toDouble(),
      closeTo((expected as num).toDouble(), 1e-12),
      reason: reason,
    );
  }
}

void main() {
  // The Python generator is intentionally independent of the Dart grader. A
  // regenerated fixture must pass real backend schema validation and grading.
  final fixture = readFixture('../../data/offline/grading_cases.json');
  final content = readFixture('assets/offline/content.json');
  final questions = (content['questions'] as List).cast<Json>();
  final bank = fixture['bank_correct_answers'] as Json;

  for (final item in (fixture['cases'] as List).cast<Json>()) {
    test('backend grading parity: ${item['name']}', () {
      final actual = gradeOfflineQuestion(
        item['question'] as Json,
        List<String>.from(item['answer'] as List),
      );
      final expected = item['expected'] as Json;
      for (final field in ['score', 'max_score']) {
        expectScore(actual[field], expected[field], '${item['name']}: $field');
      }
      final actualContext = Map<String, dynamic>.of(actual)
        ..remove('score')
        ..remove('max_score');
      final expectedContext = Map<String, dynamic>.of(expected)
        ..remove('score')
        ..remove('max_score');
      expect(actualContext, expectedContext);
    });
  }

  test('backend oracle covers every active bundled question exactly once', () {
    expect(questions.length, fixture['question_count']);
    expect(questions.map((q) => q['id']).toSet(), bank.keys.toSet());
    final types = <String, int>{};
    for (final question in questions) {
      final type = question['type'] as String;
      types[type] = (types[type] ?? 0) + 1;
    }
    expect(types, fixture['question_types']);
  });

  for (final type in (fixture['question_types'] as Json).keys) {
    test(
      'all $type questions agree with backend for correct and empty answers',
      () {
        for (final question in questions.where((q) => q['type'] == type)) {
          final id = question['id'] as String;
          final expected = bank[id] as Json;
          var answer = List<String>.from(question['correct_answer'] as List);
          if (type == 'numeric' || type == 'short_answer') {
            answer = answer.take(1).toList();
          }
          final correct = gradeOfflineQuestion(question, answer);
          final empty = gradeOfflineQuestion(question, const []);
          expectScore(
            correct['score'],
            expected['score'],
            '$id: correct score',
          );
          expectScore(
            empty['score'],
            expected['empty_score'],
            '$id: empty score',
          );
          expectScore(
            correct['max_score'],
            expected['max_score'],
            '$id: maximum',
          );
          expect(correct['status'], expected['status'], reason: id);
          expect(empty['status'], expected['status'], reason: id);
        }
      },
    );
  }
}
