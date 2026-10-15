import 'package:flutter_test/flutter_test.dart';
import 'package:kho_hoc_mobile/repository.dart';
import 'package:kho_hoc_mobile/study_progress.dart';

Json record(
  String id, {
  required num? score,
  num max = 1,
  String topic = 'fraction',
  int grade = 5,
}) => {
  'id': id,
  'backend_url': '/api',
  'questions': [
    {
      'id': 'q',
      'grade': grade,
      'subject': 'toan',
      'topic': topic,
      'topic_name': 'Phân số',
    },
  ],
  'result': {
    'score': score,
    'max_score': max,
    'details': [
      {'question_id': 'q', 'score': score, 'max_score': max},
    ],
  },
};

void main() {
  test(
    'Latest correct answer removes earlier mistake without inflating topic counts',
    () {
      final progress = StudyProgress.fromHistory([
        record('new', score: 1),
        record('old', score: 0),
      ]);
      expect(progress.completed, 2);
      expect(progress.averagePercent, 50);
      expect(progress.topics.single.attempted, 1);
      expect(progress.topics.single.percent, 100);
      expect(progress.topics.single.wrongQuestionIds, isEmpty);
    },
  );
  test(
    'Partial credit needs practice; pending and legacy rows do not create fake mastery',
    () {
      final progress = StudyProgress.fromHistory([
        record('partial', score: 0.5),
        record('pending', score: null, topic: 'essay', grade: 6),
        {
          'id': 'legacy',
          'result': {'score': 2, 'max_score': 2},
        },
      ]);
      expect(progress.completed, 3);
      expect(progress.graded, 2);
      expect(progress.topics.single.percent, 50);
      expect(progress.topics.single.wrongQuestionIds, ['q']);
      expect(progress.topics.single.correct, 0);
    },
  );
  test('Deleting latest result recalculates from retained history', () {
    final old = record('old', score: 0);
    expect(
      StudyProgress.fromHistory([
        record('new', score: 1),
        old,
      ]).topics.single.correct,
      1,
    );
    expect(StudyProgress.fromHistory([old]).topics.single.wrongQuestionIds, [
      'q',
    ]);
    expect(StudyProgress.fromHistory([]).averagePercent, isNull);
  });
}
