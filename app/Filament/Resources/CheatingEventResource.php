<?php

namespace App\Filament\Resources;

use App\Filament\Resources\CheatingEventResource\Pages;
use App\Filament\Resources\CheatingEventResource\RelationManagers;
use App\Models\CheatingEvent;
use Filament\Forms;
use Filament\Forms\Components\DateTimePicker;
use Filament\Forms\Components\FileUpload;
use Filament\Forms\Components\TextInput;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Columns\ImageColumn;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\SoftDeletingScope;

class CheatingEventResource extends Resource
{
    protected static ?string $model = CheatingEvent::class;

    protected static ?string $modelLabel = 'Bukti Kecurangan';

    protected static ?string $slug = 'kecurangan';

    protected static ?string $navigationIcon = 'heroicon-o-rectangle-stack';

    public static function form(Form $form): Form
    {
        return $form
            // ->columns(1)
            ->schema([
                DateTimePicker::make('created_at')
                    ->label('Waktu')
                    ->displayFormat('H:m:s, d F Y')
                    ->locale('id'),

                TextInput::make('name')
                    ->label('Nama'),

                FileUpload::make('image')
                    ->directory('cheating-events')
                    ->image()
                    ->deletable(false)
                    ->openable(true),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                TextColumn::make('created_at')
                    ->label('Waktu')
                    ->dateTime('H:m:s, d F Y', 'Asia/Jakarta')
                    ->sortable(),

                ImageColumn::make('image')
                    ->label('Bukti')
                    ->height(120)
                    ->checkFileExistence(false),

                TextColumn::make('name')
                    ->label('Nama')
                    ->searchable()
                    ->sortable(),

            ])
            ->filters([
                //
            ])
            ->actions([
                Tables\Actions\ViewAction::make(),
                Tables\Actions\DeleteAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                ]),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListCheatingEvents::route('/'),
            // 'create' => Pages\CreateCheatingEvent::route('/create'),
            'view' => Pages\ViewCheatingEvent::route('/{record}'),
            // 'edit' => Pages\EditCheatingEvent::route('/{record}/edit'),
        ];
    }
}
