"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

// Types
interface Feature {
  icon: React.ReactNode;
  title: string;
  description: string;
}

interface Step {
  step: string;
  title: string;
  description: string;
}

interface FAQItem {
  question: string;
  answer: string;
}

export default function Home() {
  // Redirect to app if already logged in
  useEffect(() => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      if (token) {
        window.location.href = "/app/decks";
      }
    }
  }, []);

  // State for Mobile Menu
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // State for FAQ accordion
  const [openFaqIndex, setOpenFaqIndex] = useState<number | null>(null);

  const toggleFaq = (index: number) => {
    setOpenFaqIndex(openFaqIndex === index ? null : index);
  };

  // SVG Icons
  const Icons = {
    Brain: () => (
      <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
    Layers: () => (
      <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
    ),
    Template: () => (
      <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm0 8a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zm10 0a1 1 0 011-1h4a1 1 0 011 1v6a1 1 0 01-1 1h-4a1 1 0 01-1-1v-6z" />
      </svg>
    ),
    Edit: () => (
      <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
      </svg>
    ),
    Chart: () => (
      <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z" />
      </svg>
    ),
    Globe: () => (
      <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
      </svg>
    ),
    ArrowRight: ({ className = "w-5 h-5" }) => (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
      </svg>
    ),
    Check: () => (
      <svg className="w-5 h-5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
      </svg>
    ),
    Fire: () => (
      <svg className="w-6 h-6 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
        <path fillRule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.921-.432.753-.787 1.636-1.072 2.612a4.99 4.99 0 01-.344-1.2 1 1 0 00-1.897-.247c-.752 2.133-1.078 4.298-1.078 6.46 0 3.79 3.067 6.859 6.856 6.859a6.85 6.85 0 006.858-6.858c0-2.616-1.124-4.86-2.91-6.446a1 1 0 00-1.62.78 4.001 4.001 0 01-.77 2.378c-.287.41-.65.733-1.073.957a4.96 4.96 0 01-1.664.557c-.122.02-.245.033-.369.04a1.004 1.004 0 00-.775-.233 1 1 0 00-.472-.816c-.033-.021-.065-.043-.096-.067A1 1 0 0012 11c0-.498-.103-.993-.3-1.455a7.973 7.973 0 00-.632-1.229 1 1 0 001.327-.478c.412-.843.766-1.782.97-2.735a1 1 0 00-.97-2.55z" clipRule="evenodd" />
      </svg>
    ),
    ChevronDown: ({ className = "w-5 h-5 text-gray-500" }) => (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
      </svg>
    ),
    Menu: () => (
      <svg className="w-6 h-6 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    ),
    X: () => (
      <svg className="w-6 h-6 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
      </svg>
    )
  };

  const features: Feature[] = [
    {
      icon: <Icons.Brain />,
      title: "Lặp lại ngắt quãng (SM-2)",
      description: "Thuật toán học thông minh . Thẻ khó xuất hiện thường xuyên, thẻ đã thuộc được giãn lịch ôn tập. Giúp ghi nhớ dài hạn, tiết kiệm thời gian tối đa."
    },
    {
      icon: <Icons.Layers />,
      title: "Bộ thẻ phân cấp",
      description: "Tổ chức từ vựng theo chủ đề, cấp độ, hoặc sách giáo khoa. Hỗ trợ tạo các bộ thẻ con không giới hạn cấp độ, dễ dàng kéo thả để cấu trúc lại lộ trình học."
    },
    {
      icon: <Icons.Template />,
      title: "Mẫu thẻ tùy chỉnh",
      description: "Tự thiết kế bố cục thẻ theo ý muốn. Thêm các trường dữ liệu tùy chỉnh như: phát âm (IPA), từ loại, định nghĩa tiếng Việt, câu ví dụ, âm thanh phát âm."
    },
    {
      icon: <Icons.Edit />,
      title: "Cloze Deletion & Điền từ",
      description: "Tạo thẻ dạng ẩn từ trong câu {{c1::cloze}} thông minh hoặc luyện viết chính tả trực tiếp bằng trường gõ đáp án — lý tưởng để học ngữ pháp và collocations."
    },
    {
      icon: <Icons.Chart />,
      title: "Thống kê & Đo lường",
      description: "Theo dõi tiến độ học tập chi tiết qua biểu đồ phân phối thẻ (Mới, Đang học, Ôn tập), tỷ lệ đoán đúng và lịch sử hoạt động hàng ngày của bạn."
    },
    {
      icon: <Icons.Globe />,
      title: "Bộ thẻ cộng đồng",
      description: "Khám phá và sử dụng hàng ngàn bộ thẻ chất lượng từ cộng đồng người học Raki: IELTS, TOEIC, SAT, từ vựng thông dụng, tiếng Anh chuyên ngành."
    }
  ];

  const steps: Step[] = [
    {
      step: "01",
      title: "Tạo hoặc chọn bộ thẻ",
      description: "Tự tạo bộ thẻ tiếng Anh cá nhân hoặc lưu các bộ thẻ chất lượng được chia sẻ miễn phí từ thư viện cộng đồng."
    },
    {
      step: "02",
      title: "Học & Đánh giá hàng ngày",
      description: "Mỗi ngày Raki sẽ tự động lọc ra các thẻ mới và thẻ cần ôn tập. Trả lời và tự đánh giá độ khó: Lại, Khó, Tốt, Dễ để hệ thống tính toán chu kỳ lặp lại tiếp theo."
    },
    {
      step: "03",
      title: "Theo dõi & Tích lũy",
      description: "Xem các biểu đồ thống kê trực quan về số thẻ bạn đã thuộc và duy trì chuỗi ngày học liên tục (streak) để tạo thói quen học tập bền vững."
    }
  ];

  const faqs: FAQItem[] = [
    {
      question: "Raki hoạt động dựa trên nguyên lý nào?",
      answer: "Raki hoạt động dựa trên phương pháp Lặp lại ngắt quãng (Spaced Repetition) kết hợp thuật toán SM-2. Thay vì học nhồi nhét, hệ thống sẽ nhắc nhở bạn ôn tập từ vựng ngay trước thời điểm bạn chuẩn bị quên nó. Khoảng cách giữa các lần ôn tập sẽ tăng dần nếu bạn nhớ tốt, giúp kiến thức đi sâu vào trí nhớ dài hạn."
    },
    {
      question: "Raki có điểm gì khác so với các ứng dụng học từ vựng khác?",
      answer: "Raki giữ nguyên lõi sức mạnh (Spaced Repetition, Custom Note Type, Cloze Deletion) nhưng mang lại giao diện hiện đại, thân thiện, dễ sử dụng hơn ngay trên nền tảng web. Bạn có thể học ngay trên trình duyệt mà không cần cài đặt phần mềm phức tạp, đồng thời dễ dàng kết nối với kho tài liệu cộng đồng trực tuyến."
    },
    {
      question: "Tôi có thể tự tạo bộ thẻ học riêng theo nhu cầu không?",
      answer: "Hoàn toàn có thể. Raki hỗ trợ bạn tạo bộ thẻ riêng, tùy chỉnh các trường thông tin (từ vựng, nghĩa, IPA, ví dụ, hình ảnh) và thiết kế giao diện hiển thị mặt trước / mặt sau của thẻ ."
    },
    {
      question: "Ứng dụng Raki có miễn phí không?",
      answer: "Đúng vậy, Raki hoàn toàn miễn phí cho các chức năng học tập cơ bản: tự tạo thẻ, học theo thuật toán lặp lại ngắt quãng, thống kê học tập và tải các bộ thẻ cộng đồng chia sẻ."
    }
  ];

  return (
    <div className="min-h-screen bg-[#f4f7f6] text-slate-800 font-sans flex flex-col antialiased">
      {/* Header / Navbar */}
      <header className="sticky top-0 z-50 bg-[#1e293b] border-b border-[#334155] shadow-md">
        <div className="max-w-[96%] mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center text-2xl font-bold text-slate-100 tracking-tight">
              <span className="text-[#60a5fa] mr-0.5">ra</span>ki
            </Link>

            {/* Desktop Nav Links */}
            <nav className="hidden md:flex items-center gap-6">
              <a href="#features" className="text-slate-300 hover:text-white hover:bg-slate-700/50 px-3 py-1.5 rounded-md text-sm font-medium transition duration-200">
                Tính năng
              </a>
              <a href="#workflow" className="text-slate-300 hover:text-white hover:bg-slate-700/50 px-3 py-1.5 rounded-md text-sm font-medium transition duration-200">
                Quy trình học
              </a>
              <a href="#stats" className="text-slate-300 hover:text-white hover:bg-slate-700/50 px-3 py-1.5 rounded-md text-sm font-medium transition duration-200">
                Thống kê
              </a>
              <a href="#faq" className="text-slate-300 hover:text-white hover:bg-slate-700/50 px-3 py-1.5 rounded-md text-sm font-medium transition duration-200">
                Hỏi đáp
              </a>
              
            </nav>
          </div>

          {/* Action Buttons */}
          <div className="hidden md:flex items-center gap-4">
            <a
              href="/app/login"
              className="text-slate-300 hover:text-white text-sm font-medium transition duration-200"
            >
              Đăng nhập
            </a>
            <a
              href="/app/register"
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition duration-200 shadow-sm shadow-blue-500/20"
            >
              Bắt đầu miễn phí
            </a>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-700 focus:outline-none"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <Icons.X /> : <Icons.Menu />}
          </button>
        </div>

        {/* Mobile Navigation Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-[#1e293b] border-t border-[#334155] px-4 py-4 space-y-3 shadow-lg">
            <a
              href="#features"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-slate-300 hover:text-white py-2 font-medium border-b border-slate-700/50"
            >
              Tính năng
            </a>
            <a
              href="#workflow"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-slate-300 hover:text-white py-2 font-medium border-b border-slate-700/50"
            >
              Quy trình học
            </a>
            <a
              href="#stats"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-slate-300 hover:text-white py-2 font-medium border-b border-slate-700/50"
            >
              Thống kê
            </a>
            <a
              href="#faq"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-slate-300 hover:text-white py-2 font-medium border-b border-slate-700/50"
            >
              Hỏi đáp
            </a>
            <a
              href="/app/community"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-slate-300 hover:text-white py-2 font-medium border-b border-slate-700/50"
            >
              Cộng đồng
            </a>
            <div className="pt-2 flex flex-col gap-2">
              <a
                href="/app/login"
                className="w-full text-center text-slate-300 hover:text-white py-2 font-medium rounded-lg border border-[#334155]"
              >
                Đăng nhập
              </a>
              <a
                href="/app/register"
                className="w-full text-center bg-blue-500 hover:bg-blue-600 text-white py-2 font-semibold rounded-lg shadow-sm"
              >
                Đăng ký miễn phí
              </a>
            </div>
          </div>
        )}
      </header>

      {/* Hero Section */}
      <section className="bg-white border-b border-[#dfe7f2] py-16 md:py-24 relative overflow-hidden">
        {/* Soft background blue blur blobs */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full bg-blue-50/60 blur-3xl pointer-events-none -z-10" />

        <div className="max-w-6xl mx-auto px-6 grid md:grid-cols-12 gap-12 items-center">
          {/* Hero text content */}
          <div className="md:col-span-7 text-center md:text-left space-y-6">
            <div className="inline-flex items-center gap-2 bg-blue-50 border border-blue-200 px-3 py-1.5 rounded-full text-sm font-medium text-blue-700">
              <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
              Flashcard học tiếng Anh chuyên sâu 
            </div>
            <h1 className="text-4xl sm:text-5xl font-extrabold text-[#141a2d] leading-[1.15] tracking-tight">
              Làm chủ từ vựng <br className="hidden sm:inline" />
              tiếng Anh với <span className="text-blue-600">Raki</span>
            </h1>
            <p className="text-lg text-slate-600 max-w-xl mx-auto md:mx-0 leading-relaxed">
              Phương pháp lặp lại ngắt quãng (Spaced Repetition) giúp tối ưu hóa khả năng ghi nhớ dài hạn của não bộ. Học ít hơn, nhớ lâu hơn, đạt hiệu quả gấp 3 lần.
            </p>
            <div className="flex flex-wrap justify-center md:justify-start gap-4">
              <a
                href="/app/register"
                className="bg-blue-500 hover:bg-blue-600 text-white px-8 py-3.5 rounded-xl font-semibold shadow-md shadow-blue-500/10 hover:shadow-blue-500/25 transition duration-200 flex items-center gap-2 group"
              >
                Bắt đầu miễn phí ngay
                <Icons.ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </a>
              <a
                href="/app/login"
                className="bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 px-8 py-3.5 rounded-xl font-semibold transition duration-200"
              >
                Đăng nhập
              </a>
            </div>
          </div>

          {/* Hero visual card placeholder */}
          <div className="md:col-span-5 flex justify-center">
            <div className="w-full max-w-sm bg-white border border-[#dfe7f2] rounded-2xl shadow-xl shadow-slate-200/80 p-6 relative overflow-hidden transition-all duration-300 hover:shadow-2xl">
              <div className="flex items-center justify-between text-xs text-slate-400 font-medium pb-4 border-b border-slate-100">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-blue-500" />
                  Bộ thẻ: IELTS Vocabulary
                </span>
                <span>Thẻ số 12/80</span>
              </div>

              {/* Card display content */}
              <div className="py-8 text-center space-y-4">
                <span className="bg-blue-50 text-blue-700 text-xs font-semibold px-2.5 py-1 rounded-full uppercase tracking-wider">
                  Adjective
                </span>
                <h3 className="text-3xl font-bold text-[#141a2d] tracking-tight">ubiquitous</h3>
                <p className="text-sm text-slate-400 font-mono">/juːˈbɪkwɪtəs/</p>
                <div className="pt-4 border-t border-dashed border-slate-100 space-y-2.5">
                  <p className="text-base font-semibold text-slate-700">
                    Có mặt ở khắp mọi nơi, phổ biến
                  </p>
                  <p className="text-xs text-slate-500 italic max-w-[280px] mx-auto leading-relaxed">
                    &ldquo;Mobile phones are now <span className="text-blue-600 font-semibold">ubiquitous</span> in our daily lives.&rdquo;
                  </p>
                </div>
              </div>

              {/* Study rating buttons mock */}
              <div className="grid grid-cols-4 gap-1.5 pt-4 border-t border-slate-100">
                <button className="bg-red-50 hover:bg-red-100 text-red-600 text-xs font-semibold py-2 rounded-lg border border-red-200/50 transition">
                  Lại <span className="block text-[9px] font-normal text-red-500">1m</span>
                </button>
                <button className="bg-amber-50 hover:bg-amber-100 text-amber-600 text-xs font-semibold py-2 rounded-lg border border-amber-200/50 transition">
                  Khó <span className="block text-[9px] font-normal text-amber-500">6m</span>
                </button>
                <button className="bg-blue-50 hover:bg-blue-100 text-blue-600 text-xs font-semibold py-2 rounded-lg border border-blue-200/50 transition">
                  Tốt <span className="block text-[9px] font-normal text-blue-500">10m</span>
                </button>
                <button className="bg-emerald-50 hover:bg-emerald-100 text-emerald-600 text-xs font-semibold py-2 rounded-lg border border-emerald-200/50 transition">
                  Dễ <span className="block text-[9px] font-normal text-emerald-500">4d</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 max-w-6xl mx-auto px-6">
        <div className="text-center max-w-2xl mx-auto space-y-4 mb-16">
          <h2 className="text-3xl font-bold text-[#141a2d] tracking-tight sm:text-4xl">
            Tối ưu cho việc học ngoại ngữ
          </h2>
          <p className="text-slate-600 leading-relaxed">
            Raki mang đến trải nghiệm học tập hiện đại, mượt mà trên nền tảng web.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feat, idx) => (
            <div
              key={idx}
              className="bg-white border border-[#dfe7f2] p-6 rounded-2xl shadow-sm transition duration-300 hover:shadow-md hover:border-blue-200 group"
            >
              <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center mb-5 group-hover:scale-110 transition duration-200">
                {feat.icon}
              </div>
              <h3 className="text-lg font-bold text-[#141a2d] mb-2">{feat.title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed">{feat.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Workflow Section */}
      <section id="workflow" className="bg-white border-y border-[#dfe7f2] py-20">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto space-y-4 mb-16">
            <h2 className="text-3xl font-bold text-[#141a2d] tracking-tight sm:text-4xl">
              Chỉ 3 bước đơn giản để bắt đầu
            </h2>
            <p className="text-slate-600 leading-relaxed">
              Bạn không cần cài đặt phức tạp, không cần tài liệu hướng dẫn dày đặc. Học ngay lập tức.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 relative">
            {/* Visual connector line for desktop */}
            <div className="hidden md:block absolute top-12 left-1/6 right-1/6 h-0.5 bg-blue-100 -z-10" style={{ left: '16.66%', right: '16.66%' }} />

            {steps.map((step, idx) => (
              <div key={idx} className="bg-[#f4f7f6] p-8 rounded-2xl border border-[#dfe7f2] space-y-4 text-center md:text-left">
                <span className="inline-block text-4xl font-extrabold text-blue-500/20 tracking-wider">
                  {step.step}
                </span>
                <h3 className="text-xl font-bold text-[#141a2d]">{step.title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Statistics Mockup Section */}
      <section id="stats" className="py-20 max-w-6xl mx-auto px-6">
        <div className="grid md:grid-cols-12 gap-12 items-center">
          <div className="md:col-span-6 space-y-6">
            <h2 className="text-3xl font-bold text-[#141a2d] tracking-tight sm:text-4xl">
              Thống kê trực quan, <br />
              định lượng tiến trình học
            </h2>
            <p className="text-slate-600 leading-relaxed">
              Nhìn thấy bản thân tiến bộ mỗi ngày chính là động lực lớn nhất. Raki tự động ghi lại quá trình học tập của bạn, chuyển hóa những nỗ lực thầm lặng thành các con số và biểu đồ sinh động.
            </p>
            <ul className="space-y-3">
              {[
                "Theo dõi chuỗi ngày học liên tục (streak) để duy trì thói quen.",
                "Biết chính xác số lượng từ vựng ở từng trạng thái học.",
                "Đo lường thời gian thực tế bạn đã dành ra để tích lũy kiến thức."
              ].map((item, idx) => (
                <li key={idx} className="flex items-start gap-3">
                  <span className="mt-1 flex-shrink-0">
                    <Icons.Check />
                  </span>
                  <span className="text-slate-700 font-medium text-sm sm:text-base">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="md:col-span-6 flex justify-center">
            {/* Visual statistics card */}
            <div className="w-full max-w-md bg-white border border-[#dfe7f2] rounded-2xl shadow-lg p-6 space-y-6">
              <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                <div>
                  <h4 className="font-bold text-slate-800">Tiến độ học tập</h4>
                  <p className="text-xs text-slate-400">Dữ liệu cập nhật hôm nay</p>
                </div>
                <div className="flex items-center gap-1 bg-amber-50 border border-amber-200 px-3 py-1 rounded-full text-amber-700 font-bold text-sm">
                  <Icons.Fire />
                  15 ngày
                </div>
              </div>

              {/* Card Distribution Bar */}
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-semibold text-slate-500">
                  <span>Phân bổ trạng thái thẻ</span>
                  <span>Tổng: 545 thẻ</span>
                </div>
                <div className="h-4 w-full rounded-full bg-slate-100 flex overflow-hidden">
                  <div className="bg-blue-500 h-full" style={{ width: "22%" }} title="Mới: 120 thẻ (22%)" />
                  <div className="bg-amber-500 h-full" style={{ width: "8%" }} title="Đang học: 45 thẻ (8%)" />
                  <div className="bg-emerald-500 h-full" style={{ width: "70%" }} title="Đã thuộc: 380 thẻ (70%)" />
                </div>
                {/* Legends */}
                <div className="flex flex-wrap gap-4 pt-1 text-xs text-slate-500 font-medium justify-between">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded bg-blue-500" />
                    Mới: 120 (22%)
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded bg-amber-500" />
                    Đang học: 45 (8%)
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded bg-emerald-500" />
                    Đã thuộc: 380 (70%)
                  </span>
                </div>
              </div>

              {/* Weekly mock activity chart */}
              <div className="space-y-3">
                <div className="text-xs font-semibold text-slate-500">Thống kê số thẻ ôn tập trong tuần</div>
                <div className="grid grid-cols-7 gap-2 items-end h-28 pt-2">
                  {[45, 60, 30, 80, 95, 40, 110].map((val, idx) => {
                    const days = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"];
                    return (
                      <div key={idx} className="flex flex-col items-center gap-1.5 h-full justify-end">
                        <div
                          className="bg-blue-100 hover:bg-blue-500 rounded-t-md w-full transition-all duration-300 relative group cursor-pointer"
                          style={{ height: `${(val / 120) * 100}%` }}
                        >
                          <div className="absolute -top-7 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-[10px] px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap z-10 pointer-events-none">
                            {val} thẻ
                          </div>
                        </div>
                        <span className="text-[10px] text-slate-400 font-semibold">{days[idx]}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Accordion Section */}
      <section id="faq" className="bg-white border-y border-[#dfe7f2] py-20">
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl font-bold text-[#141a2d] tracking-tight sm:text-4xl">
              Giải đáp thắc mắc
            </h2>
            <p className="text-slate-600 leading-relaxed">
              Các thông tin cơ bản giúp bạn nhanh chóng hiểu rõ về Raki.
            </p>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, idx) => {
              const isOpen = openFaqIndex === idx;
              return (
                <div
                  key={idx}
                  className="bg-[#f4f7f6] border border-[#dfe7f2] rounded-xl overflow-hidden transition"
                >
                  <button
                    onClick={() => toggleFaq(idx)}
                    className="w-full px-6 py-4 flex items-center justify-between text-left font-bold text-slate-800 hover:text-blue-600 transition"
                  >
                    <span>{faq.question}</span>
                    <Icons.ChevronDown className={`w-5 h-5 transition-transform duration-200 ${isOpen ? 'rotate-180 text-blue-600' : ''}`} />
                  </button>
                  <div
                    className={`transition-all duration-300 ease-in-out overflow-hidden ${isOpen ? 'max-h-60 border-t border-slate-200/60' : 'max-h-0'}`}
                  >
                    <div className="p-6 text-sm sm:text-base text-slate-500 leading-relaxed bg-white">
                      {faq.answer}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Call To Action (CTA) Section */}
      <section className="bg-gradient-to-br from-blue-50 via-white to-blue-50/30 py-20 border-b border-[#dfe7f2]">
        <div className="max-w-4xl mx-auto px-6 text-center space-y-8">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#141a2d] tracking-tight">
            Sẵn sàng học tiếng Anh vượt trội?
          </h2>
          <p className="text-slate-600 max-w-xl mx-auto leading-relaxed">
            Chỉ với 5 phút mỗi ngày cùng Raki, bạn sẽ ngạc nhiên với khối lượng từ vựng tiếng Anh mình tích lũy được sau 1 tháng. Đăng ký tài khoản miễn phí và học ngay hôm nay.
          </p>
          <div className="flex justify-center gap-4 flex-wrap">
            <a
              href="/app/register"
              className="bg-blue-500 hover:bg-blue-600 text-white px-8 py-4 rounded-xl font-bold transition duration-200 shadow-md shadow-blue-500/10 hover:shadow-blue-500/25"
            >
              Tạo tài khoản miễn phí
            </a>
            <a
              href="/app/login"
              className="bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 px-8 py-4 rounded-xl font-bold transition duration-200"
            >
              Đăng nhập ngay
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#1e293b] text-slate-400 py-12 border-t border-[#334155]">
        <div className="max-w-[96%] mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-2 text-center md:text-left">
            <div className="text-xl font-bold text-white tracking-tight">
              <span className="text-[#60a5fa] mr-0.5">ra</span>ki
            </div>
            <p className="text-xs text-slate-400">
              © {new Date().getFullYear()} raki. Ứng dụng flashcard thông minh cho người học tiếng Anh.
            </p>
          </div>

          <div className="flex gap-6 text-sm font-medium">
            <a href="/app/community" className="hover:text-white transition">Cộng đồng</a>
            <a href="/app/login" className="hover:text-white transition">Đăng nhập</a>
            <a href="/app/register" className="hover:text-white transition">Đăng ký</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
