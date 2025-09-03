# 2. Tech-README.md  
**Как технологически реализованы потребительские свойства**

---

## 1. Лента постов и пагинация  
**Пользователь видит**: карточки, кнопка «Далее».  
**Как реализовано**:  
- `FeedView` (`ListView`) с `paginate_by = 3`.  
- Django ORM строит SQL-запрос вида  
  `... ORDER BY created_at DESC LIMIT 3 OFFSET 0`.  
- В шаблоне `feed.html` цикл `{% for post in page_obj %}` + `{% include 'pagination.html' %}`, который выводит `page_obj.has_previous/next` и ссылки `?page=N`.  
- При подписке используется второй queryset:  
  `Post.objects.filter(author__followers_set__user=request.user)` — это JOIN по таблице `subscriptions`.

---

## 2. Лайки без перезагрузки  
**Пользователь нажимает сердечко — счётчик мгновенно меняется**.  
**Как реализовано**:  
- `like_api` — Django view, обёрнута в `@require_POST` и `@csrf_exempt`.  
- Внутри:  
  ```python
  like, created = Like.objects.get_or_create(user=request.user, post=post)
  if not created:
      like.delete()
  return JsonResponse({"liked": created, "count": post.likes.count()})
  ```  
- На фронтенде jQuery:  
  ```js
  $.post(`/post/${id}/like/`, {csrfmiddlewaretoken: csrftoken})
    .done(data => btn.toggleClass('btn-primary').html(data.count));
  ```  
- База защищена уникальным индексом `(user, post)` → нельзя поставить два лайка.

---

## 3. Комментарии: дерево + ограничение времени  
**Пользователь пишет / отвечает / удаляет**.  
**Как реализовано**:  
- Модель `Comment` с FK `parent = models.ForeignKey('self')`.  
- В `PostDetailView` строится словарь:  
  ```python
  tree = {}
  for c in comments_qs:
      tree.setdefault(c.parent_id or 0, []).append(c)
  ```  
- Рендер рекурсивно через `{% include 'comments.html' %}` — дерево без лишних SQL-запросов.  
- **Ограничение 1 час**:  
  ```python
  def can_edit(user):
      return user == self.author and (now - self.created_at).total_seconds() < 3600
  ```  
- Удаление через AJAX DELETE:  
  `$.ajax({url: '/comment/123/', method: 'DELETE', headers: {'X-CSRFToken': token}})`.

---

## 4. Подписки  
**Пользователь подписывается → видит только нужных авторов**.  
**Как реализовано**:  
- Модель `Subscription(user, author)` c unique-констрейнтом.  
- Во view `FeedView` (подписки) строится фильтр:  
  `author__followers_set__user=request.user` — это SQL-INNER JOIN.  
- При POST-запросе из формы `FollowForm` используется `bulk_create` для множественной подписки.

---

## 5. Личные сообщения  
**Пользователь открывает диалог → чат без перезагрузки**.  
**Как реализовано**:  
- Модель `Thread(user1, user2)` гарантирует уникальность:  
  `unique_together(user1, user2)` + сортировка ID.  
- `ChatView` (CreateView) — POST-создание сообщения и редирект на ту же страницу.  
- Счётчик непрочитанных:  
  `thread.messages.filter(is_read=False).exclude(sender=request.user).count()`  
  выводится в шапке через AJAX polling каждые 30 сек (`setInterval(fetchNotifications)`).

---

## 6. Уведомления  
**Иконка колокольчика с красным счётчиком**.  
**Как реализовано**:  
- Django signals (`post_save`) создают `Notification` через GenericForeignKey:  
  ```python
  Notification.objects.get_or_create(
      recipient=post.author,
      actor=user,
      verb=Notification.LIKE,
      target_ct=ContentType.objects.get_for_model(post),
      target_id=post.pk
  )
  ```  
- AJAX-endpoint `/notifications/api/unread/` отдаёт JSON `{count: N, list: [...]}`.  
- Кнопка «Прочитано» — POST `/notifications/mark/<id>/`.

---

## 7. Поиск мгновенный  
**Поле в шапке, результат без перезагрузки**.  
**Как реализовано**:  
- `SearchView` (ListView) принимает `GET ?q=`, строит Q-запрос:  
  `Q(title__icontains=q) | Q(description__icontains=q) | ...`.  
- Подсветка совпадений через custom filter `|highlight:query` — RegExp в шаблоне.

---

## 8. Статика и медиа  
- Bootstrap + jQuery подгружаются через CDN → браузер кеширует.  
- Изображения (`ImageField`) сохраняются в `MEDIA_ROOT`, отдаются через `MEDIA_URL`.  
- В production используется `collectstatic` + WhiteNoise или S3.

---

## 9. Безопасность и производительность  
- `@login_required` / `@user_passes_test` на всех POST/DELETE view.  
- CSRF-токены на AJAX (берутся из `<meta name="csrf-token">`).  
- База защищена уникальными constraint’ами и проверками `can_edit`.  
- ORM-оптимизации: `select_related('author')`, `only(...)` в queryset’ах.

---

## 10. Масштабирование
- Заменить SQLite → PostgreSQL (одна строка в `DATABASES`).  
- Добавить `django-redis` для кеша страниц.  
- Для realtime-чата подключить `channels` + Redis WebSocket — код view останется почти тем же.

---