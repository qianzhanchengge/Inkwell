<template>
  <div class="blog-article">
    <el-card v-loading="loading" shadow="never" class="blog-article__card">
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

        <MarkdownPreview :content="article.content" />
      </template>
    </el-card>

    <el-card v-if="article" shadow="never" class="blog-article__related">
      <template #header>相关文章</template>
      <div v-if="related.length" class="blog-article__related-list">
        <router-link v-for="r in related" :key="r.id" :to="`/blog/articles/${r.id}`">
          {{ r.title }}
        </router-link>
      </div>
      <el-empty v-else description="暂无相关文章" :image-size="50" />
    </el-card>

    <el-card v-if="article" shadow="never" class="blog-article__comments">
      <template #header>评论（{{ commentCount }}）</template>
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
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import MarkdownPreview from '@/components/MarkdownPreview.vue'
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
  max-width: 820px;
  margin: 0 auto;
  padding: 24px 16px;
}
.blog-article__card {
  margin-bottom: 16px;
}
.blog-article__title {
  margin: 0 0 12px;
  font-size: 26px;
}
.blog-article__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  color: #909399;
  font-size: 13px;
  margin-bottom: 16px;
}
.blog-article__author {
  color: #409eff;
}
.blog-article__summary {
  color: #606266;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 16px;
}
.blog-article__actions {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}
.blog-article__related {
  margin-bottom: 16px;
}
.blog-article__related-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  a {
    color: #606266;
    &:hover {
      color: #409eff;
    }
  }
}
</style>
