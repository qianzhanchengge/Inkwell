<template>
  <div class="blog-article">
    <article class="blog-article__card">
      <template v-if="article">
        <h1 class="blog-article__title">{{ article.title }}</h1>
        <div class="blog-article__meta">
          <span v-if="article.author?.nickname" class="blog-article__author">
            {{ article.author.nickname }}
          </span>
          <span v-if="article.published_at">发布于 {{ formatDateTime(article.published_at) }}</span>
          <span>阅读 {{ article.view_count }}</span>
          <span>点赞 {{ article.like_count }}</span>
          <span>评论 {{ commentCount }}</span>
          <span>分享 {{ article.share_count ?? 0 }}</span>
        </div>

        <div v-if="article.summary" class="blog-article__summary">{{ article.summary }}</div>

        <div class="blog-article__actions">
          <LikeButton
            :article-id="article.id"
            :liked="article.is_liked"
            :like-count="article.like_count"
            @change="onLikeChange"
          />
          <FavoriteButton
            :article-id="article.id"
            :favorited="article.is_favorited"
            @change="onFavoriteChange"
          />
          <ShareButton :article-id="article.id" />
        </div>

        <div class="blog-article__content">
          <MarkdownPreview :content="article.content" />
        </div>
      </template>
      <el-skeleton v-else-if="loading" :rows="8" animated />
      <el-empty v-else description="文章不存在或已下架" />
    </article>

    <BlogWidget v-if="article" title="相关文章">
      <div v-if="related.length" class="blog-article__related-list">
        <router-link v-for="r in related" :key="r.id" :to="`/blog/articles/${r.id}`">
          {{ r.title }}
        </router-link>
      </div>
      <el-empty v-else description="暂无相关文章" :image-size="50" />
    </BlogWidget>

    <BlogWidget v-if="article" :title="`评论（${commentCount}）`">
      <CommentInput
        :reply-to="replyTo"
        :submitting="submitting"
        @submit="onSubmitComment"
        @cancel-reply="replyTo = null"
      />
      <CommentList
        :comments="comments"
        :current-user-id="currentUserId"
        @reply="onReply"
        @delete="onDeleteComment"
      />
    </BlogWidget>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import MarkdownPreview from '@/components/MarkdownPreview.vue'
import BlogWidget from '@/components/BlogWidget.vue'
import LikeButton from '@/components/LikeButton.vue'
import FavoriteButton from '@/components/FavoriteButton.vue'
import ShareButton from '@/components/ShareButton.vue'
import CommentList from '@/components/CommentList.vue'
import CommentInput from '@/components/CommentInput.vue'
import { getBlogArticle } from '@/api/blogArticle'
import { getRelatedArticles } from '@/api/blog'
import { getComments, createComment, deleteComment } from '@/api/comment'
import { useBlogUserStore } from '@/stores/blogUser'
import { useLogin } from '@/composables/useLogin'
import type { Article } from '@/types/article'
import type { Comment } from '@/types/comment'
import type { RelatedArticle } from '@/types/blog'
import { formatDateTime } from '@/utils/format'

const route = useRoute()
const blogUserStore = useBlogUserStore()
const { ensureLogin } = useLogin()

const loading = ref(false)
const article = ref<Article | null>(null)
const related = ref<RelatedArticle[]>([])
const comments = ref<Comment[]>([])
const commentCount = ref(0)
const currentUserId = ref<number | null>(null)
const submitting = ref(false)
const replyTo = ref<Comment | null>(null)

const articleId = route.params.id as string

async function loadArticle() {
  loading.value = true
  try {
    article.value = await getBlogArticle(articleId)
    commentCount.value = article.value.comment_count ?? 0
  } catch {
    // 错误提示已统一处理
  } finally {
    loading.value = false
  }
}

async function loadRelated() {
  try {
    related.value = await getRelatedArticles(articleId, 5)
  } catch {
    // 失败不阻塞
  }
}

async function loadComments() {
  try {
    const data = await getComments(articleId, { page: 1, page_size: 100 })
    comments.value = data.items
    commentCount.value = data.total
  } catch {
    // 失败不阻塞
  }
}

async function loadCurrentUser() {
  // 只认博客登录态：工作台已登录不代表博客已登录
  if (!blogUserStore.token) {
    currentUserId.value = null
    return
  }
  try {
    if (!blogUserStore.userInfo) {
      await blogUserStore.fetchMe()
    }
    currentUserId.value = blogUserStore.userInfo?.id ?? null
  } catch {
    currentUserId.value = null
  }
}

function onLikeChange(v: { liked: boolean; like_count: number }) {
  if (article.value) {
    article.value.is_liked = v.liked
    article.value.like_count = v.like_count
  }
}

function onFavoriteChange(v: { favorited: boolean }) {
  if (article.value) {
    article.value.is_favorited = v.favorited
  }
}

function onReply(comment: Comment) {
  replyTo.value = comment
}

async function onSubmitComment(content: string) {
  // 发表评论需博客登录（工作台已登录也需单独登录博客）
  const ok = await ensureLogin()
  if (!ok) return
  submitting.value = true
  try {
    const payload = replyTo.value
      ? {
          content,
          parent_id: replyTo.value.id,
          reply_to_user_id: replyTo.value.user_id
        }
      : { content }
    await createComment(articleId, payload)
    ElMessage.success('评论成功')
    replyTo.value = null
    await loadComments()
  } catch {
    // 错误提示已统一处理
  } finally {
    submitting.value = false
  }
}

async function onDeleteComment(comment: Comment) {
  try {
    await ElMessageBox.confirm('确定删除这条评论吗？', '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteComment(comment.id)
    ElMessage.success('已删除')
    await loadComments()
  } catch {
    // 错误提示已统一处理
  }
}

onMounted(() => {
  loadArticle()
  loadRelated()
  loadComments()
  loadCurrentUser()
})
</script>

<style scoped lang="scss">
.blog-article {
  max-width: var(--blog-reading);
  margin: 0 auto;
  padding: 40px 20px 56px;
}

.blog-article__card {
  background: var(--blog-surface);
  border-radius: var(--blog-radius);
  box-shadow: var(--blog-shadow-sm);
  padding: 28px 30px 32px;
  margin-bottom: 18px;
}

.blog-article__title {
  margin: 0 0 14px;
  font-size: clamp(28px, 4vw, 38px);
  font-weight: 700;
  line-height: 1.25;
  letter-spacing: -0.02em;
  color: var(--blog-ink);
  text-wrap: balance;
}

.blog-article__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  color: var(--blog-ink-mute);
  font-size: 13px;
  font-variant-numeric: tabular-nums;
  margin-bottom: 20px;
}

/* 元信息之间用中点分隔 */
.blog-article__meta > span + span::before {
  content: '·';
  margin: 0 7px;
  opacity: 0.55;
}

.blog-article__author {
  color: var(--blog-accent);
}

.blog-article__summary {
  padding: 12px 14px;
  border-left: 3px solid var(--blog-accent);
  background: var(--blog-accent-soft);
  border-radius: var(--blog-radius-sm);
  color: var(--blog-ink-soft);
  font-size: 14px;
  line-height: 1.7;
  margin-bottom: 20px;
}

.blog-article__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 24px;
}

/* 阅读区：16px / 1.85 / 约 68 字符 */
.blog-article__content {
  font-size: 16px;
  line-height: 1.85;
  letter-spacing: 0.01em;
  color: var(--blog-ink);

  :deep(p),
  :deep(li) {
    max-width: 68ch;
  }

  :deep(img) {
    max-width: 100%;
    border-radius: var(--blog-radius-sm);
  }

  :deep(pre) {
    border-radius: var(--blog-radius-sm);
    overflow-x: auto;
  }

  :deep(code) {
    font-variant-numeric: tabular-nums;
  }

  :deep(a) {
    color: var(--blog-accent);
    text-decoration: underline;
    text-underline-offset: 2px;
  }
}

.blog-article__related-list {
  display: flex;
  flex-direction: column;

  a {
    padding: 8px 0;
    font-size: 14px;
    color: var(--blog-ink-soft);
    border-bottom: 1px solid var(--blog-line);
    transition: color 0.2s, transform 0.2s;

    &:last-child {
      border-bottom: 0;
    }

    &:hover {
      color: var(--blog-accent);
      transform: translateX(2px);
    }

    &:active {
      transform: translateX(2px) translateY(1px);
    }
  }
}
</style>
