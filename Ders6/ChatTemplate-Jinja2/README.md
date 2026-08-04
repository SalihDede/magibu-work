# Custom Chat Template (Jinja2)

Magibu Ders6 ödevi: system/user/assistant rollerini ve tool-calling'i doğru
sarmalayan, sıfırdan tasarlanmış bir Jinja2 chat template.

## Format

Hazır bir modelin (ChatML, Llama3 vb.) formatını kopyalamak yerine kendi özel
tokenlarımızı kullandım:

| Token | Ne işe yarar |
|---|---|
| `&lt;\|system\|&gt;` / `&lt;\|user\|&gt;` / `&lt;\|assistant\|&gt;` | rol açılışı |
| `&lt;\|end\|&gt;` | mesajın kapanışı |
| `&lt;\|available_tools\|&gt;` | sistem mesajına eklenen, modelin kullanabileceği araçların JSON listesi |
| `&lt;\|tool_call\|&gt;` ... `&lt;\|end_tool_call\|&gt;` | assistant'ın çağırdığı fonksiyon + argümanlar |
| `&lt;\|tool_result\|&gt;` | tool'dan dönen gerçek veri |

Bir assistant mesajı hem düz metin hem de birden fazla `tool_call` içerebilir
(çoklu araç çağrısı destekleniyor). `tool` rolündeki mesajlar `name` alanıyla
hangi aracın sonucu olduğunu taşır.

## Bulgular

- Jinja2'de `tojson` filtresi kütüphaneye dahil değil (Flask/transformers
  ekliyor), saf Jinja2 ile kullanırken kendim eklemem gerekti.
- `trim_blocks`/`lstrip_blocks` gibi environment ayarları template'in kendi
  whitespace kontrolüyle (`{%- -%}`) çakışıyor; ikisini birden kullanınca
  bloklar birbirine yapıştı. Whitespace kontrolünü tamamen template dosyasının
  içine gömüp environment'ı varsayılan ayarlarda bıraktım — böylece template
  hangi ortamda render edilirse edilsin (transformers, düz jinja2 vs.) aynı
  çıktıyı verir.
- `transformers.chat_template_utils` de tool tanımlarını benzer şekilde JSON
  olarak sisteme enjekte ediyor, bizim `&lt;\|available_tools\|&gt;` yaklaşımımız da
  aynı mantığı izliyor.

## Örnek

`test_template.py`, ikinci ödevdeki THY seyahat asistanı senaryosunu
simüle ediyor: kullanıcı "Eyfel Kulesi'ne gitmek istiyorum" diyor, model
sırayla `search_wikipedia` → `check_balance` → `search_flights` araçlarını
çağırıp gerçek tool sonuçlarına dayanan bir gün planı çıkarıyor.

```bash
python test_template.py
```

Kısaltılmış çıktı:

```
<|system|>
Sen bir THY seyahat asistanisin. Sadece tool'lardan donen gercek verileri kullan...
<|available_tools|>
[{"name": "search_wikipedia", ...}, {"name": "check_balance", ...}, ...]
<|end|><|user|>
Eyfel Kulesi'ne gitmek istiyorum, bana gunluk bir plan yapar misin?
<|end|><|assistant|>
<|tool_call|>
{"name": "search_wikipedia", "arguments": {"query": "Eyfel Kulesi"}}
<|end_tool_call|>
<|end|><|tool_result|>
{"name": "search_wikipedia", "content": {"title": "Eyfel Kulesi", "city": "Paris", "country": "Fransa"}}
<|end|>...
<|end|><|assistant|>
Bakiyen 12.500 TRY, TK1823 sefer sayili 2026-09-10 10:15 Paris ucusu 4.200 TRY...
<|end|>
```
