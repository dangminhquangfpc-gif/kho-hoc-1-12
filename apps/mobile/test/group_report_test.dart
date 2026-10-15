import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kho_hoc_mobile/account_screen.dart';
import 'package:kho_hoc_mobile/repository.dart';
import 'accounts_test.dart' show SchoolApi;

class ReportApi extends SchoolApi {
  String? exported;
  @override
  Future<List<Json>> classroomGroups() async => [
    {'id': 'g1', 'name': 'Nhóm Toán', 'join_code': 'code', 'student_ids': []},
  ];
  @override
  Future<String> groupResultsCsv(String id) async {
    exported = id;
    return '\ufeffNhóm,Tên đăng nhập\r\nNhóm Toán,hocsinh\r\n';
  }
}

void main() {
  testWidgets('Teacher exports current group; student has no export controls', (
    tester,
  ) async {
    final api = ReportApi();
    String? copied;
    tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
      SystemChannels.platform,
      (call) async {
        if (call.method == 'Clipboard.setData') copied = call.arguments['text'];
        return null;
      },
    );
    addTearDown(
      () => tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
        SystemChannels.platform,
        null,
      ),
    );
    Widget screen(bool student) => ProviderScope(
      overrides: [apiProvider.overrideWithValue(api)],
      child: MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: GroupPanel(key: ValueKey(student), student: student),
          ),
        ),
      ),
    );
    await tester.pumpWidget(screen(false));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Nhóm Toán'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Sao chép bảng điểm CSV'));
    await tester.pumpAndSettle();
    expect(api.exported, 'g1');
    expect(copied, contains('Nhóm Toán,hocsinh'));
    await tester.pumpWidget(screen(true));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Nhóm Toán'));
    await tester.pumpAndSettle();
    expect(find.text('Sao chép bảng điểm CSV'), findsNothing);
  });
}
