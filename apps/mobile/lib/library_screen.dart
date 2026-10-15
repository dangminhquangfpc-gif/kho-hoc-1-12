import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';
import 'main.dart' show Shell, Failure;
import 'repository.dart';

typedef DocumentFilter = ({
  int grade,
  String subject,
  String search,
  int semester,
  String textbook,
  String kind,
  String topic,
  String period,
  int year,
  String section,
});
final documentsProvider = FutureProvider.family<List<Json>, DocumentFilter>(
  (ref, f) => ref.watch(apiProvider).documents({
    'grade': f.grade,
    'subject': f.subject,
    'search': f.search,
    'section': f.section,
    if (f.semester != 0) 'semester': f.semester,
    if (f.textbook.isNotEmpty) 'textbook': f.textbook,
    if (f.kind.isNotEmpty) 'kind': f.kind,
    if (f.topic.isNotEmpty) 'topic': f.topic,
    if (f.period.isNotEmpty) 'assessment_period': f.period,
    if (f.year != 0) 'exam_year': f.year,
  }),
);

final curriculumProvider =
    FutureProvider.family<Json, ({int grade, String subject})>(
      (ref, f) => ref.watch(apiProvider).curriculum(f.grade, f.subject),
    );

class LibraryScreen extends ConsumerStatefulWidget {
  const LibraryScreen({
    super.key,
    this.examMode = false,
    this.initialGrade = 1,
    this.initialSubject = 'toan',
  });
  final bool examMode;
  final int initialGrade;
  final String initialSubject;
  @override
  ConsumerState<LibraryScreen> createState() => _LibraryState();
}

class _LibraryState extends ConsumerState<LibraryScreen> {
  int grade = 1, semester = 0;
  String subject = 'toan', search = '', textbook = '', kind = '', topic = '';
  String period = '';
  int year = 0;
  bool favoritesOnly = false, recentOnly = false;
  @override
  void initState() {
    super.initState();
    grade = widget.initialGrade;
    subject = widget.initialSubject;
  }

  @override
  Widget build(BuildContext context) {
    final filter = (
      grade: grade,
      subject: subject,
      search: search,
      semester: semester,
      textbook: textbook,
      kind: kind,
      topic: topic,
      period: period,
      year: year,
      section: widget.examMode ? 'exams' : 'lessons',
    );
    final documents = ref.watch(documentsProvider(filter));
    final curriculum = widget.examMode
        ? null
        : ref.watch(curriculumProvider((grade: grade, subject: subject)));
    final subjects = ref.watch(subjectsProvider(grade));
    final prefs = ref.watch(preferencesProvider).asData?.value;
    final favorites = prefs?.getStringList('favorite_documents') ?? [];
    final recent = prefs?.getStringList('recent_documents') ?? [];
    return Shell(
      title: widget.examMode
          ? 'Đề kiểm tra từ nguồn Internet'
          : 'Bài học và bài tập',
      index: widget.examMode ? 2 : 1,
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            widget.examMode
                ? 'Đề giữa kỳ, cuối kỳ và tốt nghiệp. Các đề nguồn ngoài mở ở trang gốc.'
                : 'Chọn phần học để đọc kiến thức, cách làm, ví dụ và bài tập có lời giải.',
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<int>(
            initialValue: grade,
            decoration: const InputDecoration(labelText: 'Lớp học'),
            items: [
              for (int i = 1; i <= 12; i++)
                DropdownMenuItem(value: i, child: Text('Lớp $i')),
            ],
            onChanged: (v) => setState(() {
              grade = v!;
              subject = 'toan';
            }),
          ),
          subjects.when(
            data: (items) => DropdownButtonFormField<String>(
              key: ValueKey(grade),
              initialValue: subject,
              decoration: const InputDecoration(labelText: 'Môn học'),
              items: items
                  .map(
                    (s) => DropdownMenuItem(
                      value: s['id'] as String,
                      child: Text(s['name']),
                    ),
                  )
                  .toList(),
              onChanged: (v) => setState(() => subject = v!),
            ),
            loading: () => const LinearProgressIndicator(),
            error: (_, _) =>
                Failure(retry: () => ref.invalidate(subjectsProvider(grade))),
          ),
          TextField(
            decoration: const InputDecoration(
              labelText: 'Tìm tài liệu',
              prefixIcon: Icon(Icons.search),
            ),
            onChanged: (v) => setState(() => search = v),
          ),
          DropdownButtonFormField<int>(
            initialValue: semester,
            decoration: const InputDecoration(labelText: 'Học kỳ'),
            items: const [
              DropdownMenuItem(value: 0, child: Text('Tất cả')),
              DropdownMenuItem(value: 1, child: Text('Học kỳ 1')),
              DropdownMenuItem(value: 2, child: Text('Học kỳ 2')),
            ],
            onChanged: (v) => setState(() => semester = v!),
          ),
          DropdownButtonFormField<String>(
            initialValue: textbook,
            decoration: const InputDecoration(labelText: 'Bộ sách'),
            items: const [
              DropdownMenuItem(value: '', child: Text('Tất cả')),
              DropdownMenuItem(
                value: 'independent',
                child: Text('Không phụ thuộc bộ sách'),
              ),
              DropdownMenuItem(
                value: 'ket_noi_tri_thuc',
                child: Text('Kết nối tri thức'),
              ),
              DropdownMenuItem(
                value: 'chan_troi_sang_tao',
                child: Text('Chân trời sáng tạo'),
              ),
              DropdownMenuItem(value: 'canh_dieu', child: Text('Cánh Diều')),
              DropdownMenuItem(
                value: 'national_common',
                child: Text('Đề quốc gia dùng chung'),
              ),
            ],
            onChanged: (v) => setState(() => textbook = v!),
          ),
          if (widget.examMode)
            DropdownButtonFormField<String>(
              initialValue: kind,
              decoration: const InputDecoration(labelText: 'Loại tài liệu'),
              items: const [
                DropdownMenuItem(value: '', child: Text('Tất cả')),
                DropdownMenuItem(
                  value: 'study_notes',
                  child: Text('Ghi chú học tập'),
                ),
                DropdownMenuItem(value: 'worksheet', child: Text('Bài tập')),
                DropdownMenuItem(value: 'reference', child: Text('Tham khảo')),
                DropdownMenuItem(value: 'exam', child: Text('Đề kiểm tra')),
              ],
              onChanged: (v) => setState(() => kind = v!),
            ),
          if (widget.examMode)
            DropdownButtonFormField<String>(
              initialValue: period,
              decoration: const InputDecoration(
                labelText: 'Đợt kiểm tra / ôn tập',
              ),
              items: const [
                DropdownMenuItem(value: '', child: Text('Tất cả')),
                DropdownMenuItem(
                  value: 'midterm_1',
                  child: Text('Giữa học kỳ 1'),
                ),
                DropdownMenuItem(
                  value: 'final_1',
                  child: Text('Cuối học kỳ 1'),
                ),
                DropdownMenuItem(
                  value: 'midterm_2',
                  child: Text('Giữa học kỳ 2'),
                ),
                DropdownMenuItem(
                  value: 'final_2',
                  child: Text('Cuối học kỳ 2'),
                ),
                DropdownMenuItem(
                  value: 'graduation',
                  child: Text('Tốt nghiệp THPT'),
                ),
                DropdownMenuItem(
                  value: 'review',
                  child: Text('Ôn tập / củng cố'),
                ),
              ],
              onChanged: (value) => setState(() => period = value!),
            ),
          if (widget.examMode)
            TextField(
              decoration: const InputDecoration(
                labelText: 'Năm đề thi (để trống xem tất cả)',
              ),
              keyboardType: TextInputType.number,
              onChanged: (value) =>
                  setState(() => year = int.tryParse(value) ?? 0),
            ),
          if (widget.examMode)
            const Text(
              'Đề tốt nghiệp quốc gia dùng chung cho các bộ sách. Liên kết Internet cần mạng và có thể yêu cầu tài khoản ở trang nguồn.',
            ),
          TextField(
            decoration: const InputDecoration(labelText: 'Chương/chủ đề'),
            onChanged: (v) => setState(() => topic = v),
          ),
          if (!widget.examMode && curriculum != null)
            curriculum.when(
              data: (book) => Card(
                child: ExpansionTile(
                  title: Text(
                    book['unit_count'] == null
                        ? 'Chưa xác minh mục lục sách này'
                        : 'Mục lục: ${book["authored_count"]}/${book["unit_count"]} phần có bài học',
                  ),
                  subtitle: const Text(
                    'Mục lục nguồn tham khảo; đang đối chiếu nhà xuất bản và các ấn bản.',
                  ),
                  children: [
                    for (final unit in (book['units'] as List? ?? []))
                      ListTile(
                        title: Text(unit['title']),
                        subtitle: Text(
                          unit['document_id'] == null
                              ? 'Chưa có bài hướng dẫn và luyện tập trong app'
                              : 'Có hướng dẫn và luyện tập; chờ thẩm định chuyên môn',
                        ),
                        trailing: Icon(
                          unit['document_id'] == null
                              ? Icons.pending_outlined
                              : Icons.menu_book,
                        ),
                        onTap: unit['document_id'] == null
                            ? null
                            : () => Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) =>
                                      DocumentScreen(id: unit['document_id']),
                                ),
                              ),
                      ),
                  ],
                ),
              ),
              loading: () => const LinearProgressIndicator(),
              error: (_, _) => const Text('Chưa tải được mục lục.'),
            ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            children: [
              FilterChip(
                label: const Text('Chỉ yêu thích'),
                selected: favoritesOnly,
                onSelected: (v) => setState(() => favoritesOnly = v),
              ),
              FilterChip(
                label: const Text('Đọc gần đây'),
                selected: recentOnly,
                onSelected: (v) => setState(() => recentOnly = v),
              ),
            ],
          ),
          const SizedBox(height: 12),
          documents.when(
            data: (items) {
              final rows = items
                  .where(
                    (d) =>
                        (!favoritesOnly || favorites.contains(d['id'])) &&
                        (!recentOnly || recent.contains(d['id'])),
                  )
                  .toList();
              if (recentOnly) {
                rows.sort(
                  (a, b) => recent
                      .indexOf(a['id'])
                      .compareTo(recent.indexOf(b['id'])),
                );
              }
              if (rows.isEmpty) {
                return Padding(
                  padding: const EdgeInsets.all(20),
                  child: Text(
                    widget.examMode
                        ? 'Chưa có đề phù hợp với bộ lọc.'
                        : 'Chưa có bài học gắn đúng mục lục SGK cho bộ lọc này. Xem các phần còn thiếu trong mục lục phía trên.',
                  ),
                );
              }
              return Column(
                children: rows
                    .map(
                      (d) => Card(
                        child: ListTile(
                          title: Text(d['title']),
                          subtitle: Text(d['summary'] ?? ''),
                          onTap: () async {
                            await Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => DocumentScreen(id: d['id']),
                              ),
                            );
                            if (mounted) {
                              setState(() {});
                            }
                          },
                          trailing: IconButton(
                            tooltip: favorites.contains(d['id'])
                                ? 'Bỏ yêu thích'
                                : 'Lưu tài liệu yêu thích',
                            icon: Icon(
                              favorites.contains(d['id'])
                                  ? Icons.bookmark
                                  : Icons.bookmark_outline,
                            ),
                            onPressed: prefs == null
                                ? null
                                : () async {
                                    final next = [...favorites];
                                    if (next.contains(d['id'])) {
                                      next.remove(d['id']);
                                    } else {
                                      next.add(d['id']);
                                    }
                                    await prefs.setStringList(
                                      'favorite_documents',
                                      next,
                                    );
                                    if (mounted) {
                                      setState(() {});
                                    }
                                  },
                          ),
                        ),
                      ),
                    )
                    .toList(),
              );
            },
            loading: () => const Padding(
              padding: EdgeInsets.all(24),
              child: Center(child: CircularProgressIndicator()),
            ),
            error: (_, _) =>
                Failure(retry: () => ref.invalidate(documentsProvider(filter))),
          ),
        ],
      ),
    );
  }
}

class DocumentScreen extends ConsumerStatefulWidget {
  const DocumentScreen({super.key, required this.id});
  final String id;
  @override
  ConsumerState<DocumentScreen> createState() => _DocumentState();
}

class _DocumentState extends ConsumerState<DocumentScreen> {
  late Future<Json> document;
  String? message;
  @override
  void initState() {
    super.initState();
    document = load();
  }

  Future<Json> load() async {
    final d = await ref.read(apiProvider).document(widget.id);
    final p = await SharedPreferences.getInstance();
    final recent = [
      widget.id,
      ...(p.getStringList('recent_documents') ?? []).where(
        (id) => id != widget.id,
      ),
    ];
    await p.setStringList('recent_documents', recent.take(30).toList());
    return d;
  }

  Future<void> openSource(String value) async {
    final uri = Uri.tryParse(value);
    if (uri == null || uri.scheme != 'https' || uri.userInfo.isNotEmpty) return;
    try {
      if (!await launchUrl(
        uri,
        mode: LaunchMode.platformDefault,
        webOnlyWindowName: '_blank',
      )) {
        throw StateError('Unavailable');
      }
    } catch (_) {
      if (mounted) {
        setState(() => message = 'Không mở được nguồn gốc của tài liệu.');
      }
    }
  }

  Future<void> openPdf(Json d, bool download) async {
    final uri = ref
        .read(apiProvider)
        .publicUrl(d['file_url'] ?? '/documents/${widget.id}/file')
        .replace(queryParameters: download ? {'download': 'true'} : {});
    try {
      if (!await launchUrl(
        uri,
        mode: LaunchMode.platformDefault,
        webOnlyWindowName: '_blank',
      )) {
        throw StateError('Unavailable');
      }
    } catch (_) {
      if (mounted) {
        setState(
          () => message =
              'Không mở được PDF. Kiểm tra kết nối và ứng dụng xem PDF.',
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Tài liệu học tập')),
    body: FutureBuilder<Json>(
      future: document,
      builder: (context, s) {
        if (s.hasError) {
          return Failure(retry: () => setState(() => document = load()));
        }
        if (!s.hasData) {
          return const Center(child: CircularProgressIndicator());
        }
        final d = s.data!;
        final catalog =
            ref.watch(subjectsProvider(d['grade'] as int)).asData?.value ?? [];
        final subjectName =
            catalog
                .where((row) => row['id'] == d['subject'])
                .map((row) => row['name'])
                .firstOrNull ??
            'Môn học';
        final licenseName = d['license'] == 'original_content'
            ? 'Nội dung tự biên soạn'
            : d['license'];
        final updated = DateTime.tryParse(d['updated_at'] as String);
        final updatedLabel = updated == null
            ? 'Chưa có ngày cập nhật'
            : '${updated.day}/${updated.month}/${updated.year}';
        return ListView(
          padding: const EdgeInsets.all(24),
          children: [
            Text(d['title'], style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 12),
            Text('Lớp ${d['grade']} · $subjectName · ${d['topic']}'),
            Text('Tác giả: ${d['author']}'),
            Text('Nguồn: ${d['source_name']}'),
            Text('Quyền sử dụng: $licenseName'),
            const Text('Trạng thái: Đang hiển thị trong bản thử'),
            Text('Cập nhật: $updatedLabel'),
            if (d['exam_year'] != null) Text('Năm đề thi: ${d["exam_year"]}'),
            if (d['source_verified_on'] != null)
              Text('Kiểm tra nguồn: ${d["source_verified_on"]}'),
            if (d['access_notice'] != null && d['access_notice'] != '')
              Text(d['access_notice']),
            if (d['resource_scope'] == 'collection')
              const Text(
                'Liên kết tới một bộ tài liệu/đề, chưa phải từng đề riêng lẻ.',
              ),
            const Divider(),
            for (final section in (d['sections'] as List? ?? [])) ...[
              if ((section['heading'] as String).contains('Lời giải bài tập') ||
                  (section['heading'] as String).contains('Đáp án tự kiểm tra'))
                ExpansionTile(
                  title: Text(section['heading']),
                  expandedCrossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(16),
                      child: SizedBox(
                        width: double.infinity,
                        child: DocumentText(section['text']),
                      ),
                    ),
                  ],
                )
              else ...[
                Text(
                  section['heading'],
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 8),
                DocumentText(section['text']),
                const SizedBox(height: 20),
              ],
            ],
            if (d['source_url'] != null)
              TextButton.icon(
                onPressed: () => openSource(d['source_url']),
                icon: const Icon(Icons.open_in_new),
                label: const Text('Mở nguồn gốc tài liệu'),
              ),
            if (d['can_view_pdf'] == true)
              FilledButton.icon(
                onPressed: () => openPdf(d, false),
                icon: const Icon(Icons.picture_as_pdf),
                label: const Text('Mở PDF'),
              ),
            if (d['can_download'] == true)
              TextButton.icon(
                onPressed: () => openPdf(d, true),
                icon: const Icon(Icons.download),
                label: const Text('Tải PDF được phép'),
              ),
            if (message != null) Text(message!),
          ],
        );
      },
    ),
  );
}

/// Authored calculation blocks keep their columns on narrow phone screens.
/// Normal paragraphs remain selectable, including the final answer.
class DocumentText extends StatelessWidget {
  const DocumentText(this.text, {super.key});
  final String text;
  @override
  Widget build(BuildContext context) {
    if (!text.contains('```')) return SelectableText(text);
    final parts = text.split('```');
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (var i = 0; i < parts.length; i++)
          if (parts[i].trim().isNotEmpty)
            if (i.isOdd)
              Container(
                margin: const EdgeInsets.symmetric(vertical: 8),
                padding: const EdgeInsets.all(12),
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                child: SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: SelectableText(
                    parts[i].replaceAll(RegExp(r'^\n|\n$'), ''),
                    style: const TextStyle(
                      fontFamily: 'monospace',
                      height: 1.5,
                    ),
                  ),
                ),
              )
            else
              SelectableText(parts[i].trim()),
      ],
    );
  }
}
