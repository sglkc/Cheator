<?php

use App\Http\Controllers\CheatingEventController;
use Illuminate\Support\Facades\Route;

Route::post('/cheating-events', [CheatingEventController::class, 'store']);
