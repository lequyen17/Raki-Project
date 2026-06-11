export const metadata = {
  title: "Raki — Học tiếng Anh với Flashcard thông minh",
  description:
    "Ứng dụng flashcard với thuật toán lặp lại ngắt quãng SM-2, cloze deletion, bộ thẻ tùy chỉnh và cộng đồng — học tiếng Anh hiệu quả như Anki.",
};

const features = [
  {
    icon: "🧠",
    title: "Lặp lại ngắt quãng (SM-2)",
    description:
      "Thuật toán tương tự Anki: thẻ khó xuất hiện thường xuyên hơn, thẻ đã thuộc được lên lịch ôn tập xa hơn. Học đúng lúc, nhớ lâu hơn.",
  },
  {
    icon: "📚",
    title: "Bộ thẻ phân cấp",
    description:
      "Tổ chức từ vựng theo chủ đề, cấp độ hoặc sách giáo khoa. Kéo thả để sắp xếp, theo dõi tiến độ Mới — Đang học — Ôn tập.",
  },
  {
    icon: "✏️",
    title: "Loại ghi chú tùy chỉnh",
    description:
      "Thiết kế mẫu thẻ Anh–Việt, câu ví dụ, phát âm… với trường dữ liệu và bố cục mặt trước / mặt sau linh hoạt.",
  },
  {
    icon: "🎯",
    title: "Cloze & gõ đáp án",
    description:
      "Tạo câu điền chỗ trống với {{c1::...}} hoặc luyện viết bằng trường nhập câu trả lời — lý tưởng cho ngữ pháp và collocations.",
  },
  {
    icon: "⚡",
    title: "4 mức đánh giá",
    description:
      "Lại · Khó · Tốt · Dễ — giống Anki, giúp hệ thống điều chỉnh khoảng cách ôn tập chính xác theo khả năng nhớ của bạn.",
  },
  {
    icon: "🌐",
    title: "Bộ thẻ cộng đồng",
    description:
      "Khám phá bộ thẻ do người khác chia sẻ, thêm vào danh sách học và ôn tập ngay mà không cần tự tạo từ đầu.",
  },
];

const steps = [
  {
    step: "01",
    title: "Tạo hoặc chọn bộ thẻ",
    description:
      "Tự tạo bộ thẻ tiếng Anh hoặc lấy từ thư viện cộng đồng — TOEIC, IELTS, từ vựng hàng ngày…",
  },
  {
    step: "02",
    title: "Thêm thẻ & học mỗi ngày",
    description:
      "Mỗi ngày hệ thống đưa ra thẻ mới và thẻ đến hạn. Lật thẻ, tự kiểm tra rồi chọn mức độ nhớ.",
  },
  {
    step: "03",
    title: "Theo dõi tiến độ",
    description:
      "Xem thống kê tỷ lệ hoàn thành, phân bố thẻ và chất lượng học tập trên hồ sơ cá nhân.",
  },
];

function AppLink({ href, className, children }) {
  return (
    <a href={href} target="_parent" rel="noopener noreferrer" className={className}>
      {children}
    </a>
  );
}

export default function IntroPage() {
  return (
    <div className="min-h-full bg-slate-950 text-slate-100">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div
          className="pointer-events-none absolute inset-0 opacity-40"
          style={{
            background:
              "radial-gradient(ellipse 80% 60% at 50% -20%, #3b82f6 0%, transparent 60%)",
          }}
        />
        <div className="relative mx-auto max-w-5xl px-6 py-20 sm:py-28">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-slate-700 bg-slate-900/80 px-4 py-1.5 text-sm text-slate-300">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            Flashcard thông minh cho người học tiếng Anh
          </div>

          <h1 className="mb-6 text-4xl font-bold leading-tight tracking-tight sm:text-5xl lg:text-6xl">
            Học tiếng Anh{" "}
            <span className="text-blue-400">hiệu quả hơn</span>
            <br />
            với <span className="text-blue-400">ra</span>ki
          </h1>

          <p className="mb-10 max-w-2xl text-lg leading-relaxed text-slate-400 sm:text-xl">
            Raki là ứng dụng flashcard trực tuyến lấy cảm hứng từ Anki — lặp lại
            ngắt quãng, cloze deletion, bộ thẻ tùy chỉnh và cộng đồng chia sẻ.
            Ôn tập mỗi ngày, ghi nhớ từ vựng và ngữ pháp lâu dài.
          </p>

          <div className="flex flex-wrap gap-4">
            <AppLink
              href="/register"
              className="inline-flex items-center justify-center rounded-lg bg-blue-500 px-6 py-3 text-base font-semibold text-white shadow-lg shadow-blue-500/25 transition hover:bg-blue-400"
            >
              Bắt đầu miễn phí
            </AppLink>
            <AppLink
              href="/login"
              className="inline-flex items-center justify-center rounded-lg border border-slate-600 bg-slate-900 px-6 py-3 text-base font-semibold text-slate-200 transition hover:border-slate-500 hover:bg-slate-800"
            >
              Đăng nhập
            </AppLink>
            <AppLink
              href="/community"
              className="inline-flex items-center justify-center rounded-lg px-6 py-3 text-base font-medium text-slate-400 transition hover:text-slate-200"
            >
              Khám phá cộng đồng →
            </AppLink>
          </div>

          {/* Mini study preview */}
          <div className="mt-16 rounded-2xl border border-slate-700/80 bg-slate-900/60 p-6 shadow-2xl backdrop-blur sm:p-8">
            <div className="mb-4 flex items-center justify-between text-sm text-slate-500">
              <span>Phiên học · Vocabulary Unit 3</span>
              <span>3 / 12 thẻ</span>
            </div>
            <div className="mb-2 h-1.5 overflow-hidden rounded-full bg-slate-800">
              <div className="h-full w-1/4 rounded-full bg-blue-500" />
            </div>
            <div className="mt-6 rounded-xl border border-slate-700 bg-slate-800/50 p-8 text-center">
              <p className="text-sm uppercase tracking-widest text-slate-500">
                Mặt trước
              </p>
              <p className="mt-3 text-2xl font-medium text-slate-100">
                ubiquitous
              </p>
              <p className="mt-2 text-slate-500">/juːˈbɪkwɪtəs/</p>
            </div>
            <div className="mt-6 flex flex-wrap justify-center gap-2 sm:gap-3">
              {[
                { label: "Lại", color: "bg-red-500/20 text-red-300 border-red-500/30" },
                { label: "Khó", color: "bg-orange-500/20 text-orange-300 border-orange-500/30" },
                { label: "Tốt", color: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" },
                { label: "Dễ", color: "bg-blue-500/20 text-blue-300 border-blue-500/30" },
              ].map((btn) => (
                <span
                  key={btn.label}
                  className={`rounded-lg border px-4 py-2 text-sm font-medium ${btn.color}`}
                >
                  {btn.label}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-5xl px-6 py-20">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-bold text-slate-100 sm:text-4xl">
            Mọi thứ bạn cần để học như Anki
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-slate-400">
            Không cần cài đặt phức tạp — Raki mang trải nghiệm flashcard chuyên
            sâu lên trình duyệt, tối ưu cho việc học tiếng Anh.
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <article
              key={feature.title}
              className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 transition hover:border-slate-700 hover:bg-slate-900"
            >
              <span className="text-3xl" role="img" aria-hidden="true">
                {feature.icon}
              </span>
              <h3 className="mt-4 text-lg font-semibold text-slate-100">
                {feature.title}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-400">
                {feature.description}
              </p>
            </article>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="border-y border-slate-800 bg-slate-900/30">
        <div className="mx-auto max-w-5xl px-6 py-20">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold text-slate-100 sm:text-4xl">
              Bắt đầu trong 3 bước
            </h2>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            {steps.map((item) => (
              <div key={item.step} className="relative">
                <span className="text-5xl font-bold text-slate-800">
                  {item.step}
                </span>
                <h3 className="mt-2 text-xl font-semibold text-slate-100">
                  {item.title}
                </h3>
                <p className="mt-3 text-sm leading-relaxed text-slate-400">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats / trust */}
      <section className="mx-auto max-w-5xl px-6 py-20">
        <div className="grid gap-6 rounded-2xl border border-slate-800 bg-gradient-to-br from-slate-900 to-slate-900/50 p-8 sm:grid-cols-3 sm:p-10">
          {[
            { value: "SM-2", label: "Thuật toán ôn tập đã được kiểm chứng" },
            { value: "20", label: "Thẻ mới tối đa mỗi ngày (mặc định)" },
            { value: "∞", label: "Bộ thẻ & loại ghi chú tùy chỉnh" },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="text-3xl font-bold text-blue-400">{stat.value}</p>
              <p className="mt-2 text-sm text-slate-400">{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-slate-800">
        <div className="mx-auto max-w-5xl px-6 py-20 text-center">
          <h2 className="text-3xl font-bold text-slate-100 sm:text-4xl">
            Sẵn sàng ghi nhớ từ vựng lâu hơn?
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-slate-400">
            Tạo tài khoản miễn phí, thêm bộ thẻ đầu tiên và bắt đầu phiên học
            hôm nay — chỉ vài phút mỗi ngày cũng đủ tạo khác biệt.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <AppLink
              href="/register"
              className="inline-flex items-center justify-center rounded-lg bg-blue-500 px-8 py-3.5 text-base font-semibold text-white shadow-lg shadow-blue-500/25 transition hover:bg-blue-400"
            >
              Đăng ký ngay
            </AppLink>
            <AppLink
              href="/decks"
              className="inline-flex items-center justify-center rounded-lg border border-slate-600 px-8 py-3.5 text-base font-semibold text-slate-200 transition hover:border-slate-500 hover:bg-slate-800"
            >
              Vào bộ thẻ của tôi
            </AppLink>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-950 py-8">
        <div className="mx-auto flex max-w-5xl flex-col items-center justify-between gap-4 px-6 text-sm text-slate-500 sm:flex-row">
          <p>
            © {new Date().getFullYear()}{" "}
            <span className="font-semibold text-slate-300">
              <span className="text-blue-400">ra</span>ki
            </span>
            . Học tiếng Anh bằng flashcard thông minh.
          </p>
          <div className="flex gap-6">
            <AppLink href="/community" className="transition hover:text-slate-300">
              Cộng đồng
            </AppLink>
            <AppLink href="/login" className="transition hover:text-slate-300">
              Đăng nhập
            </AppLink>
          </div>
        </div>
      </footer>
    </div>
  );
}
