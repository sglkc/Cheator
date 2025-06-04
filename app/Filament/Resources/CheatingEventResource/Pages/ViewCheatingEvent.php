<?php

namespace App\Filament\Resources\CheatingEventResource\Pages;

use App\Filament\Resources\CheatingEventResource;
use Filament\Actions;
use Filament\Resources\Pages\ViewRecord;

class ViewCheatingEvent extends ViewRecord
{
    protected static string $resource = CheatingEventResource::class;

    protected function getHeaderActions(): array
    {
        return [
            // Actions\EditAction::make(),
        ];
    }
}
