import React, { useState } from 'react';

interface TagInputProps {
    tags: string[];
    onChange: (tags: string[]) => void;
    placeholder?: string;
}

const TagInput: React.FC<TagInputProps> = ({ tags, onChange, placeholder = 'Add a dislike...' }) => {
    const [inputValue, setInputValue] = useState('');

    const addTags = (value: string) => {
        const cleanValue = value.trim();
        if (!cleanValue) return;

        // Split by commas in case user typed/pasted a list
        const newTags = cleanValue
            .split(',')
            .map((t) => t.trim().toLowerCase())
            .filter((t) => t !== '' && !tags.includes(t));

        if (newTags.length > 0) {
            onChange([...tags, ...newTags]);
        }
        setInputValue('');
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' || e.key === ',') {
            e.preventDefault();
            addTags(inputValue);
        } else if (e.key === 'Backspace' && !inputValue && tags.length > 0) {
            // Remove last tag if backspace is pressed on an empty input
            onChange(tags.slice(0, -1));
        }
    };

    const handleBlur = () => {
        addTags(inputValue);
    };

    const removeTag = (indexToRemove: number) => {
        onChange(tags.filter((_, index) => index !== indexToRemove));
    };

    return (
        <div className='tag-input-container'>
            {tags.map((tag, index) => (
                <span key={index} className='tag-chip'>
                    {tag}
                    <button
                        type='button'
                        className='tag-chip-remove'
                        onClick={() => removeTag(index)}
                        aria-label={`Remove ${tag}`}
                    >
                        ✕
                    </button>
                </span>
            ))}
            <input 
                type='text'
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                onBlur={handleBlur}
                placeholder={tags.length === 0 ? placeholder : ''}
                className='tag-inner-input'
            />
        </div>
    );
};

export default TagInput;