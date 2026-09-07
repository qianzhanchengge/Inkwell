import request from './request'
import type { Note, NoteListParams, NoteCreatePayload } from '@/types/note'
import type { PageResult } from '@/types/api'

export function getNoteList(params: NoteListParams): Promise<PageResult<Note>> {
  return request.get('/notes', { params })
}

export function getNote(id: number | string): Promise<Note> {
  return request.get(`/notes/${id}`)
}

export function createNote(data: NoteCreatePayload): Promise<Note> {
  return request.post('/notes', data)
}

export function updateNote(id: number | string, data: NoteCreatePayload): Promise<Note> {
  return request.put(`/notes/${id}`, data)
}

export function deleteNote(id: number | string): Promise<null> {
  return request.delete(`/notes/${id}`)
}

export function toggleNotePin(id: number | string): Promise<Note> {
  return request.patch(`/notes/${id}/pin`)
}

export function searchNotes(keyword: string, params?: NoteListParams): Promise<PageResult<Note>> {
  return request.get('/notes/search', { params: { ...params, keyword } })
}
