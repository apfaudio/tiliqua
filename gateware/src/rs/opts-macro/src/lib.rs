use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, DeriveInput, Data, Fields, Type, Expr, Meta};

#[proc_macro_derive(OptionSet, attributes(option))]
pub fn derive_option(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let name = &input.ident;

    let fields = match &input.data {
        Data::Struct(data) => match &data.fields {
            Fields::Named(fields) => &fields.named,
            _ => panic!("OptionSet only supports structs with named fields"),
        },
        _ => panic!("OptionSet only supports structs"),
    };

    let field_inits = fields.iter().map(|field| {
        let field_name = &field.ident;
        let field_type = &field.ty;

        let default_value = field.attrs.iter()
            .find(|attr| attr.path().is_ident("option"))
            .map(|attr| {
                attr.parse_args::<Expr>()
                    .expect("Failed to parse option argument as an expression")
            })
            .unwrap_or_else(|| syn::parse_quote! { Default::default() });

        let constructor = if is_num_option(field_type) {
            quote! { NumOption::new }
        } else if is_enum_option(field_type) {
            quote! { EnumOption::new }
        } else if is_float_option(field_type) {
            quote! { FloatOption::new }
        } else {
            panic!("Unsupported field type for OptionSet")
        };

        let field_name_str = field_name.as_ref().unwrap().to_string().replace("_","-");
        quote! {
            #field_name: #constructor(#field_name_str, #default_value)
        }
    });

    let option_fields: Vec<_> = fields.iter()
        .filter(|field| is_option_type(&field.ty))
        .map(|field| field.ident.as_ref().unwrap())
        .collect();

    let expanded = quote! {
        impl Default for #name {
            fn default() -> Self {
                Self {
                    #(#field_inits,)*
                }
            }
        }

        impl OptionView for #name {
            fn options(&self) -> OptionVec {
                OptionVec::from_slice(&[
                    #(&self.#option_fields),*
                ]).unwrap()
            }

            fn options_mut(&mut self) -> OptionVecMut {
                let mut r = OptionVecMut::new();
                #(r.push(&mut self.#option_fields).ok();)*
                r
            }
        }
    };

    TokenStream::from(expanded)
}

// Helper functions remain unchanged
fn is_num_option(ty: &Type) -> bool {
    matches!(ty, Type::Path(path) if path.path.segments.first()
        .map(|seg| seg.ident == "NumOption")
        .unwrap_or(false))
}

fn is_enum_option(ty: &Type) -> bool {
    matches!(ty, Type::Path(path) if path.path.segments.first()
        .map(|seg| seg.ident == "EnumOption")
        .unwrap_or(false))
}

fn is_float_option(ty: &Type) -> bool {
    matches!(ty, Type::Path(path) if path.path.segments.first()
        .map(|seg| seg.ident == "FloatOption")
        .unwrap_or(false))
}

fn is_option_type(ty: &Type) -> bool {
    is_num_option(ty) || is_enum_option(ty) || is_float_option(ty)
}

#[proc_macro_derive(OptionMenu, attributes(option_menu))]
pub fn option_menu_derive(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);

    let name = &input.ident;

    let fields = if let Data::Struct(data) = &input.data {
        if let Fields::Named(fields) = &data.fields {
            &fields.named
        } else {
            panic!("OptionMenu can only be derived for structs with named fields");
        }
    } else {
        panic!("OptionMenu can only be derived for structs");
    };

    let mut screen_fields = Vec::new();

    for field in fields {
        let field_name = &field.ident;
        let attrs = &field.attrs;
        for attr in attrs {
            if attr.path().is_ident("option_menu") {
                if let Ok(Meta::Path(meta_path)) = attr.parse_args() {
                    screen_fields.push((field_name.clone(), meta_path));
                }
            }
        }
    }

    let view_match_arms = screen_fields.iter().map(|(field_name, screen_value)| {
        quote! {
            #screen_value => &self.#field_name,
        }
    });

    let view_mut_match_arms = screen_fields.iter().map(|(field_name, screen_value)| {
        quote! {
            #screen_value => &mut self.#field_name,
        }
    });

    let expanded = quote! {
        impl OptionPage for #name {
            fn selected(&self) -> Option<usize> {
                self.tracker.selected
            }

            fn set_selected(&mut self, s: Option<usize>) {
                self.tracker.selected = s;
            }

            fn modify(&self) -> bool {
                self.tracker.modify
            }

            fn modify_mut(&mut self, modify: bool) {
                self.tracker.modify = modify;
            }

            fn screen(&self) -> &dyn OptionTrait {
                &self.tracker.screen
            }

            fn screen_mut(&mut self) -> &mut dyn OptionTrait {
                &mut self.tracker.screen
            }

            fn view(&self) -> &dyn OptionView {
                match self.tracker.screen.value {
                    #(#view_match_arms)*
                }
            }

            fn view_mut(&mut self) -> &mut dyn OptionView {
                match self.tracker.screen.value {
                    #(#view_mut_match_arms)*
                }
            }
        }
    };

    TokenStream::from(expanded)
}
