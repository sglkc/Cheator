<?php

namespace App\Http\Controllers;

use App\Models\CheatingEvent;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Validator;

class CheatingEventController extends Controller
{
    /**
     * Store a new cheating event with image and student name.
     *
     * @param Request $request
     * @return JsonResponse
     */
    public function store(Request $request): JsonResponse
    {
        // Validate the request
        $validator = Validator::make($request->all(), [
            'name' => 'required|string|max:255',
            'image' => 'required|image|mimes:jpeg,png,jpg,gif,svg|max:2048', // 2MB max
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Validation failed',
                'errors' => $validator->errors(),
            ], 422);
        }

        try {
            // Store the image
            $imagePath = $request->file('image')->store('cheating-events', 'public');

            // Create the cheating event
            $cheatingEvent = CheatingEvent::create([
                'name' => $request->input('name'),
                'image' => $imagePath,
            ]);

            return response()->json([
                'success' => true,
                'message' => 'Cheating event recorded successfully',
                'data' => [
                    'id' => $cheatingEvent->id,
                    'name' => $cheatingEvent->name,
                    'image' => $cheatingEvent->image,
                    'image_url' => Storage::url($cheatingEvent->image),
                    'created_at' => $cheatingEvent->created_at,
                ],
            ], 201);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to record cheating event',
                'error' => $e->getMessage(),
            ], 500);
        }
    }
}
