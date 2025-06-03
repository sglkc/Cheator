<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::get('/', fn () => view('home'))->name('home');
Route::get('/offline', fn () => view('offline'))->name('offline');

Route::fallback(fn (Request $request) => match ($request->is('assets/*')) {
    true => response()->noContent(404),
    false => view('404')
});
