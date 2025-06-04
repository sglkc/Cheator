<?php

namespace App\Filament\Resources\CheatingEventResource\Pages;

use App\Filament\Resources\CheatingEventResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditCheatingEvent extends EditRecord
{
    protected static string $resource = CheatingEventResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\DeleteAction::make(),
        ];
    }
}
