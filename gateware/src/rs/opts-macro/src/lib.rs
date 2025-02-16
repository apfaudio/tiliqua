use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, DeriveInput, Data, Fields, Type, Expr};

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
