# Veritabanı Yapılandırması Notları

Bu doküman, projenin mevcut veritabanı yapılandırmasını ve sıkça karşılaşılan senaryoları açıklamaktadır.

## Mevcut Geliştirme (Development) Ortamı Yapılandırması

Şu anki geliştirme ortamı, Docker içindeki `db` servisini **kullanmamaktadır**. Bunun yerine, uygulama doğrudan sizin **ana makinenizde (local) çalışan PostgreSQL** veritabanına bağlanacak şekilde yapılandırılmıştır.

Bu ayar, `.env` dosyasındaki `DATABASE_URL` değişkeni ile kontrol edilir:

```dotenv
# .env dosyasındaki örnek satır
DATABASE_URL=postgresql+psycopg2://postgres:1234@host.docker.internal:5434/postgres
```

- **`host.docker.internal`**: Bu özel adres, Docker konteynerinin içinden ana makinenize (host sisteminize) erişmesini sağlar.
- **`5434`**: Sizin yerel PostgreSQL sunucunuzun portu.

**Avantajı:** Bu yaklaşım, geliştirme sırasında verilerinize pgAdmin gibi yerel araçlarla kolayca erişmenizi ve yönetmenizi sağlar.

## `psql` Hatasının Açıklaması (`role ... does not exist`)

Doğrulama sırasında `docker compose exec db psql ...` komutu bir `role does not exist` hatası vermiştir. Bu bir sorun **değildir** ve nedeni şudur:

1.  **FastAPI Uygulaması:** Sizin yerel veritabanınıza (`host.docker.internal:5434`) bağlanıyor.
2.  **`psql` Komutu:** Docker ağındaki, şu anda kullanılmayan ve tam olarak yapılandırılmamış `db` konteynerine bağlanmaya çalışıyordu.

Bu iki ortam birbirinden tamamen bağımsızdır. Uygulamanın `GET /health` endpoint'inin başarılı olması, doğru veritabanına (sizin yerel veritabanınıza) bağlandığımızı kanıtlamaktadır. Kısacası, bu `psql` hatası geliştirme sürecimizi etkilememektedir.

## Üretim (Production) Ortamı

Proje canlıya alındığında (production), yapılandırma değişecektir. `docker-compose.prod.yml` gibi bir dosya kullanılarak:

- Uygulama, `host.docker.internal` yerine aynı Docker ağı içindeki `db` servisine bağlanacaktır.
- `.env.production` dosyasındaki `DATABASE_URL` şu şekilde olacaktır: `DATABASE_URL=postgresql+psycopg2://portfolio:PASSWORD@db:5432/portfolio`.

Bu, üretim ortamının kendi içinde kapalı ve güvenli bir sistem olarak çalışmasını sağlar.



---
*Bu bir test değişikliğidir.*
