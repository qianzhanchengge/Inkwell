<template>
  <div class="blog-home">
    <div class="blog-home__main">
      <div class="blog-home__toolbar">
        <el-radio-group v-model="sort" @change="onSortChange">
          <el-radio-button value="latest">最新</el-radio-button>
          <el-radio-button value="hot">热门</el-radio-button>
        </el-radio-group>
      </div>

      <div v-loading="loading">
        <ArticleCard v-for="a in articles" :key="a.id" :article="a" />
        <el-empty v-if="!loading && !articles.length" description="暂无文章" />
      </div>

      <Pagination
        :page="page"
        :page-size="pageSize"
        :total="total"
        @update:page="onPageChange"
        @update:page-size="onSizeChange"
      />
    </div>

    <aside class="blog-home__side">
      <el-card shadow="never" class="blog-home__widget">
        <template #header>分类</template>
        <div class="blog-home__cat-list">
          <router-link v-for="c in categories" :key="c.id" :to="`/blog/categories/${c.id}`">
            {{ c.name }}<span class="blog-home__count">{{ c.article_count ?? '' }}</span>
          </router-link>
          <span v-if="!categories.length" class="blog-home__empty">暂无分类</span>
        </div>
      </el-card>

      <el-card shadow="never" class="blog-home__widget">
        <template #header>标签</template>
        <TagCloud :tags="tags" />
      </el-card>

      <el-card shadow="never" class="blog-home__widget">
        <template #header>热门文章</template>
        <ol class="blog-home__hot">
          <li v-for="h in hot" :key="h.id">
            <router-link :to="`/blog/articles/${h.id}`">{{ h.title }}</router-link>
            <span class="blog-home__count">{{ h.view_count }} 阅读</span>
          </li>
          <span v-if="!hot.length" class="blog-home__empty">暂无数据</span>
        </ol>
      </el-card>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ArticleCard from '@/components/ArticleCard.vue'
import Pagination from '@/components/Pagination.vue'
import TagCloud from '@/components/TagCloud.vue'
import { getBlogFeed, getBlogCategories, getBlogTags, getBlogHot } from '@/api/blog'
import type { Article } from '@/types/article'
import type { CategoryStat, TagStat, HotArticle } from '@/types/blog'

const loading = ref(false)
const sort = ref<'latest' | 'hot'>('latest')
const articles = ref<Article[]>([])
const categories = ref<CategoryStat[]>([])
const tags = ref<TagStat[]>([])
const hot = ref<HotArticle[]>([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

async function loadFeed() {
  loading.value = true
  try {
    const data = await getBlogFeed({ page: page.value, page_size: pageSize.value, sort: sort.value })
    articles.value = data.items
    total.value = data.total
  } catch {
    // 错误提示已统一处理
  } finally {
    loading.value = false
  }
}

async function loadSidebar() {
  try {
    categories.value = await getBlogCategories()
    tags.value = await getBlogTags()
    hot.value = await getBlogHot(10)
  } catch {
    // 侧栏数据失败不阻塞正文
  }
}

function onSortChange() {
  page.value = 1
  loadFeed()
}
function onPageChange(v: number) {
  page.value = v
  loadFeed()
}
function onSizeChange(v: number) {
  pageSize.value = v
  page.value = 1
  loadFeed()
}

onMounted(() => {
  loadFeed()
  loadSidebar()
})
</script>

<style scoped lang="scss">
.blog-home {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px 16px;
  display: flex;
  gap: 20px;
}
.blog-home__main {
  flex: 1;
  min-width: 0;
}
.blog-home__toolbar {
  margin-bottom: 16px;
}
.blog-home__side {
  width: 280px;
  flex-shrink: 0;
}
.blog-home__widget {
  margin-bottom: 16px;
}
.blog-home__cat-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  a {
    color: #606266;
    padding: 4px 10px;
    background: #f5f7fa;
    border-radius: 4px;
    &:hover {
      color: #409eff;
      background: #ecf5ff;
    }
  }
}
.blog-home__hot {
  margin: 0;
  padding-left: 18px;
  li {
    margin-bottom: 10px;
    line-height: 1.5;
  }
  a {
    color: #606266;
    &:hover {
      color: #409eff;
    }
  }
}
.blog-home__count {
  color: #c0c4cc;
  font-size: 12px;
  margin-left: 4px;
}
.blog-home__empty {
  color: #c0c4cc;
  font-size: 13px;
}
</style>
