" ==============================================================================
" FILE: projectile.vim
" AUTHOR: Clay Dunston <dunstontc@gmail.com>
" License: MIT license
" Last Modified: 2018-01-11
" ==============================================================================

""
" @section Functions, functions
" Functions mostly for internal use

""
" @function(projectile#Init)
" Checks for projects.json & bookmarks.json in {g:projectile#data_dir}
" If those aren't there, or if the directory doesn't exist, it'll make them
function projectile#Init() abort
  let l:dir_path = expand(g:projectile#data_dir)
  let l:bookmark = '[{"name":"MYVIMRC","path":"' . expand("$MYVIMRC") . '","line":1,"col":1,"timestamp":"123456","description":""}]'
  let l:project  = '[{"name":"MYVIMRC","root":"' . expand("$VIMRUNTIME") . '","timestamp":"123456","vcs":false,"description":""}]'

  echo "   Set up projectile?."
  let l:confirmed_1 = confirm("-- This will overwrite any existing projectile.nvim projects and bookmarks --", "&Yes\n&No", 2)
  if l:confirmed_1 == 2
    echo "You're the boss."
  else
    if !isdirectory(l:dir_path)
      silent exe '!mkdir ' . l:dir_path.'; touch ' . l:dir_path . '/bookmarks.json ' . l:dir_path . '/projects.json'
    else
      silent exe '!touch ' . l:dir_path . '/bookmarks.json ' . l:dir_path . '/projects.json'
    endif
    silent execute writefile([l:bookmark], l:dir_path.'/bookmarks.json')
    silent execute writefile([l:project], l:dir_path.'/projects.json')
    echohl Keyword | echo "You're all set!" | echohl None
  endif
endfunction


""
" @function(projectile#CommandCompletion)
" Used by denite_source_sauce
" From 'https://stackoverflow.com/questions/21117615/how-to-obtain-command-completion-list'
function! projectile#CommandCompletion( base ) abort
  silent execute "normal! :" a:base . "\<C-a>')\<C-b>return split('\<CR>"
endfunction


function! projectile#FloatingMini() abort
  let buf = nvim_create_buf(v:false, v:true)
  call setbufvar(buf, '&signcolumn', 'no')

  let height = 1
  let width = 1
  let col = float2nr((&columns - width) / 2)

  let opts = {
        \ 'relative': 'editor',
        \ 'row': 1,
        \ 'col': col,
        \ 'width': width,
        \ 'height': height
        \ }

  call nvim_open_win(buf, v:true, opts)
endfunction

function! projectile#KillWin( winid ) abort
    execute "bdelete! " . a:winid
endfunction

function! projectile#RgHelper( winid ) abort
    Rg
    call timer_start(100000, projectile#KillWin(a:winid))
endfunction


