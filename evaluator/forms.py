"""Forms for the resume evaluator."""

from django import forms


class EvaluationForm(forms.Form):
    """Form for JD and Resume input."""

    PROVIDER_CHOICES = [
        ("openai", "OpenAI (GPT-4o)"),
        ("claude", "Anthropic (Claude)"),
    ]

    ALLOWED_EXTENSIONS = ['.pdf', '.md', '.markdown', '.txt']
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    provider = forms.ChoiceField(
        choices=PROVIDER_CHOICES,
        initial="openai",
        widget=forms.Select(attrs={"class": "form-select"}),
        label="AI 모델",
    )

    jd = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 8,
            "placeholder": "채용공고(JD)를 입력하세요...",
        }),
        label="채용공고 (JD)",
    )

    resume = forms.FileField(
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "accept": ".pdf,.md,.markdown,.txt",
        }),
        label="이력서 (필수)",
        help_text="PDF, Markdown, TXT 파일을 업로드하세요.",
    )

    career_description = forms.FileField(
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "accept": ".pdf,.md,.markdown,.txt",
        }),
        label="경력기술서 (선택)",
        help_text="PDF, Markdown, TXT 파일을 업로드하세요.",
        required=False,
    )

    def clean_resume(self):
        """Validate resume file."""
        resume = self.cleaned_data.get('resume')
        if resume:
            self._validate_file(resume, '이력서')
        return resume

    def clean_career_description(self):
        """Validate career description file."""
        career_desc = self.cleaned_data.get('career_description')
        if career_desc:
            self._validate_file(career_desc, '경력기술서')
        return career_desc

    def _validate_file(self, file, field_name):
        """Check file extension and size."""
        filename = file.name.lower()
        if not any(filename.endswith(ext) for ext in self.ALLOWED_EXTENSIONS):
            raise forms.ValidationError(
                f"{field_name}는 PDF, Markdown, TXT 파일만 업로드 가능합니다."
            )
        if file.size > self.MAX_FILE_SIZE:
            max_mb = self.MAX_FILE_SIZE // (1024 * 1024)
            raise forms.ValidationError(
                f"{field_name} 파일 크기가 {max_mb}MB를 초과합니다."
            )
