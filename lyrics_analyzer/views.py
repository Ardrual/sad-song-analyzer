from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Song
from .services import analyze_lyrics_with_gemini
from datetime import datetime


def index(request):
    if request.method == 'POST':
        lyrics = request.POST.get('lyrics', '').strip()
        
        if lyrics:
            # Analyze lyrics with Gemini API
            analysis = analyze_lyrics_with_gemini(lyrics)
            
            if analysis is None:
                # API failed - show error message instead of storing
                messages.error(request, "Sorry, there was an error analyzing your lyrics. Please try again later.")
                return redirect('index')
            
            sad_score = analysis['sad_score']
            tags = analysis['tags']
            description = analysis['description']
            
            if request.user.is_authenticated:
                # Save to database for logged-in users
                Song.objects.create(
                    user=request.user,
                    lyrics=lyrics,
                    sad_score=sad_score,
                    tags=tags,
                    description=description
                )
            else:
                # Save to session for anonymous users
                analysis_result = {
                    'lyrics': lyrics,
                    'sad_score': sad_score,
                    'tags': tags,
                    'description': description,
                    'timestamp': datetime.now().isoformat()
                }
                
                session_results = request.session.get('analysis_results', [])
                session_results.append(analysis_result)
                request.session['analysis_results'] = session_results
            
            # Redirect to prevent form resubmission
            return redirect('index')
    
    # Get results based on user authentication
    if request.user.is_authenticated:
        results = Song.objects.filter(user=request.user)
    else:
        session_results = request.session.get('analysis_results', [])
        results = sorted(session_results, key=lambda x: x['sad_score'], reverse=True)
    
    return render(request, 'lyrics_analyzer/index.html', {
        'results': results
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            
            # Auto-login after registration
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            
            return redirect('index')
    else:
        form = UserCreationForm()
    
    return render(request, 'lyrics_analyzer/register.html', {'form': form})
